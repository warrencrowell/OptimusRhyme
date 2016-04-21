import sklearn, re, nltk
import numpy as np
from twitter import *
from sklearn.feature_extraction.text import TfidfVectorizer

MIN_RESULTS = 30 # Minimum number of results needed for valid user input

class TweetMining(object):
    def __init__(self, method = "tf_idf"):
        self.twitter = None
        self.method = method
        self.setup()

    # Sets up Twitter API connection
    def setup(self):
        config = {}
        execfile("config.py", config)
        self.twitter = Twitter(auth = OAuth(config["access_key"], 
                                            config["access_secret"], 
                                            config["consumer_key"], 
                                            config["consumer_secret"]))

        if self.method == "word_embeddings":
            self.vectors = {}
            with open("glove.twitter.27B.25d.txt", 'r') as f:
                for line in f:
                    vals = line.rstrip().split(" ")
                    self.vectors[vals[0]] = np.asarray([float(x) for x in vals[1:]])

    # Returns list of at most num_words topical words for the given hashtag_set
    # For a hashtag_set [h1, h2], we perform the query "#h1 OR #h2"
    def get_topical_words(self, hashtag_set, num_words = 20):
        statuses = [t["text"] for t in self.get_query(hashtag_set)["statuses"]]
        if len(statuses) < MIN_RESULTS:
            raise Exception("Error: Not enough tweets returned by given hashtags")
        self.process_tweets(statuses)

        if self.method == "tf_idf":
            vect = TfidfVectorizer(min_df = 2, stop_words = "english", strip_accents = "ascii")
            matrix = vect.fit_transform(statuses)
            top_indices = np.argsort(vect.idf_)[::-1]
            features = vect.get_feature_names()
            return [features[i] for i in top_indices[:num_words]]

        elif self.method == "word_embeddings":
            for status in statuses:
                words = nltk.word_tokenize(status)
                for word in words:
                    if word in self.vectors:
                        topic_vector = np.add(topic_vector, self.vectors[word])
            raise Exception("Error: Word embeddings not implemented yet")

        else:
            raise Exception("Error: Invalid method specified")

    # Helper function for get_topical_words
    # Returns dict of keys "status_metadata" and "statuses" from Twitter API
    #   => "statuses" maps to a list of dicts; access "text" key to get status text
    # hashtag_set is a list of hashtags to search for (don't include #)
    def get_query(self, hashtag_set):
        query = ""
        for i in range(len(hashtag_set)):
            query += "%23" + hashtag_set[i]
            if i < len(hashtag_set) - 1:
                query += "%20OR%20"
        return self.twitter.search.tweets(q = query, 
                                          count = 100, 
                                          lang = "en", 
                                          result_type = "mixed")

    # Helper method for get_topical_words
    # Processes statuses in-place by removing irrelevant components
    def process_tweets(self, statuses):
        for i in range(len(statuses)):
            statuses[i] = re.sub(r"\S*/\S*", "", statuses[i]) # Links
            statuses[i] = re.sub(r"http\S*", "", statuses[i]) # Hanging https
            statuses[i] = re.sub(r"#", "", statuses[i]) # Hashtag symbols
            statuses[i] = re.sub(r"(RT)*( )?@\S*", "", statuses[i]) # RT, @user
            statuses[i] = re.sub(r"\S*\d+\S*", "", statuses[i]) # Numerical

            pos_info = nltk.pos_tag(nltk.word_tokenize(statuses[i]))
            statuses[i] = " ".join([word[0] for word in pos_info if "NN" in word[1]])


TM = TweetMining()
words = TM.get_topical_words(["sandwich"])
print words