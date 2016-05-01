import json

""" Input: the path of the dataset file, a list of song and line indices
    Output: List of tuples of words with highest tf-idf scores
    Given a list of song-line tuple (song_index, line_index),
    returns a list of a word-score tuple, with the word with highest score
    at the head of the list.
"""
def score_lookup(data_filename, songs_lst):
    fo = open(data_filename, 'r')
    lyrics = json.loads(fo.read())
    fo.close()

    tfidf_sum = {}
    tfidf_count = {}
    tfidf_scores = []
    for song, line in songs_lst:
        for word_idx in range(len(lyrics[song]['lyrics'][line])):
            word = lyrics[song]['lyrics'][line][word_idx]
            score = lyrics[song]['tfidf_scores'][line][word_idx]
            if word.isalpha():
                if tfidf_sum.has_key(word.lower()):
                    tfidf_sum[word.lower()] += score
                    tfidf_count[word.lower()] += 1
                else:
                    tfidf_sum[word.lower()] = score
                    tfidf_count[word.lower()] = 1
    for word, sum in tfidf_sum.items():
        tfidf_scores.append((word, sum / tfidf_count[word]))

    return sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
