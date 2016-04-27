import sklearn, re, nltk, base64, json, urllib2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import os

MIN_RESULTS = 30 # Minimum number of results needed for valid user input
BASE_SEARCH_URL = 'https://api.twitter.com/1.1/search/tweets.json?'

class TweetMining(object):
    def __init__(self, method = 'tf_idf'):
        self.twitter = None
        self.method = method
        self.setup()
        nltk.data.path.append('nltk_data/')

    # Sets up Twitter API connection
    def setup(self):
        if os.path.isfile('config.py'):
            config = {}
            execfile('config.py', config)
            consumer_key = config['consumer_key']
            consumer_secret = config['consumer_secret']
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

        if self.method == 'word_embeddings':
            self.vectors = {}
            with open('glove.twitter.27B.25d.txt', 'r') as f:
                for line in f:
                    vals = line.rstrip().split(' ')
                    self.vectors[vals[0]] = np.asarray([float(x) for x in vals[1:]])

    # Returns list of at most num_words topical words for the given hashtag_set
    def get_topical_words(self, hashtag_set, num_words = 20):
        hashtag_set = self.cleanup_tags(hashtag_set)
        statuses = [t['text'] for t in self.get_query(hashtag_set)['statuses']]
        if len(statuses) < MIN_RESULTS:
            return []

        self.process_tweets(statuses)

        if self.method == 'tf_idf':
            vect = TfidfVectorizer(min_df = 2, stop_words = 'english', strip_accents = 'ascii')
            matrix = vect.fit_transform(statuses)
            top_indices = np.argsort(vect.idf_)[::-1]
            features = vect.get_feature_names()
            return [features[i] for i in top_indices[:num_words]]

        elif self.method == 'word_embeddings':
            topic_matrix = []
            word_list = []
            for status in statuses:
                words = nltk.word_tokenize(status)
                for word in words:
                    if word in self.vectors:
                        topic_matrix.append(self.vectors[word])
                        word_list.append(word)

            np_topic_matrix = np.array(topic_matrix)
            diff_matrix = np_topic_matrix - np.mean(np_topic_matrix, axis=0)
            distances = np.sum(np.square(diff_matrix), axis=1)
            closest_indices = np.argsort(distances)[::-1]

            topical_words = []
            for ind in closest_indices:
                similar_word = word_list[ind]
                if similar_word not in topical_words:
                    topical_words.append(similar_word)
                if len(topical_words) == num_words:
                    break

            return topical_words

        else:
            raise Exception('Error: Invalid method specified')

    # Helper function for get_topical_words
    # Cleans up hashtag list input by stripping hashtags if they exist
    def cleanup_tags(hashtags):
        result = []
        for h in hashtag:
            result.append(h.strip('#').strip())
        return result

    # Helper function for get_topical_words
    # Returns dict of keys "status_metadata" and "statuses" from Twitter API
    #   => "statuses" maps to a list of dicts; access "text" key to get status text
    # hashtag_set is a list of hashtags to search for (don't include #)
    def get_query(self, hashtag_set):
        query = 'q='
        for i in range(len(hashtag_set)):
            query += '%23' + hashtag_set[i]
            if i < len(hashtag_set) - 1:
                query += '%20OR%20'

        query_url = BASE_SEARCH_URL + query + '&result_type=mixed&lang=en&count=100'
        request = urllib2.Request(query_url)
        request.add_header('Authorization', 'Bearer %s' % self.access_token)

        response = urllib2.urlopen(request)
        contents = response.read()
        return json.loads(contents)

    # Helper method for get_topical_words
    # Processes statuses in-place by removing irrelevant components
    def process_tweets(self, statuses):
        for i in range(len(statuses)):
            statuses[i] = re.sub(r'\S*/\S*', '', statuses[i]) # Links
            statuses[i] = re.sub(r'http\S*', '', statuses[i]) # Hanging https
            statuses[i] = re.sub(r'#', '', statuses[i]) # Hashtag symbols
            statuses[i] = re.sub(r'(RT)*( )?@\S*', '', statuses[i]) # RT, @user
            statuses[i] = re.sub(r'\S*\d+\S*', '', statuses[i]) # Numerical

            pos_info = nltk.pos_tag(nltk.word_tokenize(statuses[i]))
            statuses[i] = ' '.join([word[0] for word in pos_info if 'NN' in word[1]])
