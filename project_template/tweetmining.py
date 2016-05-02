import sklearn, re, nltk, base64, json, urllib2, os
import numpy as np
import cPickle as pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import os

MIN_RESULTS = 30 # Minimum number of results needed for valid user input
BASE_SEARCH_URL = 'https://api.twitter.com/1.1/search/tweets.json?'

class TweetMining(object):
    def __init__(self, method = 'tf_idf_old'):
        nltk.data.path.append('nltk_data/')
        self.method = method
        self.setup()

    # Sets up Twitter API connection
    def setup(self):
        if os.path.isfile("config.py"):
            config = {}
            execfile("config.py", config)
            consumer_key = config["consumer_key"]
            consumer_secret = config["consumer_secret"]
        elif os.path.isfile("project_template/config.py"):
            config = {}
            execfile("project_template/config.py", config)
            consumer_key = config["consumer_key"]
            consumer_secret = config["consumer_secret"]
        else:
            consumer_key = os.getenv('CONSUMER_KEY')
            consumer_secret = os.getenv('CONSUMER_SECRET')

        bearer_token = '%s:%s' % (consumer_key, consumer_secret)
        bearer_token_64 = base64.b64encode(bearer_token)

        token_request = urllib2.Request('https://api.twitter.com/oauth2/token')
        token_request.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')
        token_request.add_header('Authorization', 'Basic %s' % bearer_token_64)
        token_request.data = 'grant_type=client_credentials'

        token_response = urllib2.urlopen(token_request)
        token_contents = token_response.read()
        token_data = json.loads(token_contents)
        self.access_token = token_data['access_token']

        if os.path.isfile("smaller_pho_dict.p"):
            with open('smaller_pho_dict.p', 'rb') as handle:
                self.dict = pickle.load(handle)
        else:
            with open('project_template/smaller_pho_dict.p', 'rb') as handle:
                self.dict = pickle.load(handle)


        if self.method == 'tf_idf_new':
            if os.path.isfile("idf.pickle"):
                with open('idf.pickle', 'rb') as handle:
                    self.idf = pickle.load(handle)
            else:
                with open('project_template/idf.pickle', 'rb') as handle:
                    self.idf = pickle.load(handle)

    # Returns list of at most num_words topical words for the given hashtag_set
    def get_topical_words(self, hashtag_set, num_words = 30):
        hashtag_set = self.cleanup_tags(hashtag_set)

        if self.method == 'tf_idf_old':
            statuses = [t['text'] for t in self.get_tweets(hashtag_set, 100)]
            if len(statuses) < MIN_RESULTS:
                return []
            self.process_tweets(statuses)
            vect = TfidfVectorizer(min_df = 2, stop_words = 'english', strip_accents = 'ascii')
            matrix = vect.fit_transform(statuses)
            top_indices = np.argsort(vect.idf_)[::-1]
            features = vect.get_feature_names()
            return [features[i] for i in top_indices[:num_words]]

        elif self.method == 'tf_idf_new':
            statuses = [t['text'] for t in self.get_tweets(hashtag_set, 200 * len(hashtag_set))]
            if len(statuses) < MIN_RESULTS:
                return [], []

            self.process_tweets(statuses, nouns_only = False)

            getIDF = lambda word : self.idf[word] if word in self.idf else 0
            vect = CountVectorizer(stop_words = 'english', strip_accents = 'ascii')

            tf = vect.fit_transform([' '.join(statuses)]).toarray()
            features = vect.get_feature_names()
            idf_vals = np.array([np.log(1600000.0 / (1 + getIDF(word))) for word in features])
            tfidf = np.multiply(tf, idf_vals)

            frequencies = [(features[i], tf[0][i]) for i in np.argsort(tf[0])[::-1][:30]]

            top_indices = np.argsort(tfidf[0])[::-1]
            max_tfidf = tfidf[0][top_indices[0]]
            frequencies = [(features[i], 80 * (tfidf[0][i] / max_tfidf)) for i in top_indices[:40]]

            top_words = [(word, max_tfidf * 1.01) for word in hashtag_set if word.upper() in self.dict and word not in features]
            for i in top_indices:
                word = features[i]
                if not any(word in pair for pair in top_words) and word.upper() in self.dict:
                    top_words.append((word, tfidf[0][i]))
                if len(top_words) == num_words:
                    break

            return top_words, frequencies

        else:
            raise Exception('Error: Invalid method specified')

    # Helper function for get_topical_words
    # Cleans up hashtag list input by stripping hashtags if they exist
    def cleanup_tags(self, hashtags):
        return [h.strip(',').strip('#').strip() for h in hashtags]

    # Helper function for get_topical_words
    # Returns list of dicts; access "text" key to get status text
    # hashtag_set is a list of hashtags to search for (don't include #)
    def get_tweets(self, hashtag_set, num_tweets = 500):
        num_queries = num_tweets / 100
        extra_tweets = num_tweets % 100

        base_query = BASE_SEARCH_URL + 'q='
        for i in range(len(hashtag_set)):
            base_query += '%23' + hashtag_set[i]
            if i < len(hashtag_set) - 1:
                base_query += '%20OR%20'
        base_query += '&lang=en&result_type=recent&count=100'

        def callAPI(query_url):
            request = urllib2.Request(query_url)
            request.add_header('Authorization', 'Bearer %s' % self.access_token)
            response = urllib2.urlopen(request)
            contents = response.read()
            return json.loads(contents)

        result = []
        query = base_query
        for q in range(num_queries):
            statuses = callAPI(query)['statuses']
            if statuses == []:
                return []
            result.extend(statuses)
            minID = min([status['id'] for status in statuses])
            query = base_query + '&max_id=' + str(minID)

        if extra_tweets > 0 and not out_of_tweets:
            query = re.sub(r'&count=\d+', '', query) + '&count=' + str(extra_tweets)
            result.extend(callAPI(query)['statuses'])

        return result

    # Helper method for get_topical_words
    # Processes statuses in-place by removing irrelevant components
    def process_tweets(self, statuses, nouns_only = True):
        for i in range(len(statuses)):
            statuses[i] = re.sub(r'\S*/\S*', '', statuses[i]) # Links
            statuses[i] = re.sub(r'htt\S*', '', statuses[i]) # Hanging https
            statuses[i] = re.sub(r'#\S*', '', statuses[i]) # Hashtag symbols
            statuses[i] = re.sub(r'(RT)*( )?@\S*', '', statuses[i]) # RT, @user
            statuses[i] = re.sub(r'(RT |rt[^a-z])', '', statuses[i]) # RT/rt
            statuses[i] = re.sub(r'\S*\d+\S*', '', statuses[i]) # Numerical
            statuses[i] = re.sub(r"\w+'[^s ]+", '', statuses[i]) # Contractions
            statuses[i] = re.sub(r'&\S+;', '', statuses[i]) # HTML entities

            if nouns_only:
                pos_info = nltk.pos_tag(nltk.word_tokenize(statuses[i]))
                statuses[i] = ' '.join([word[0] for word in pos_info if 'NN' in word[1]])
