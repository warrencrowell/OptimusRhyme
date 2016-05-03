import json

""" Input: the lyrics list, the tfidf scores list, a list of song and line indices
    Output: List of tuples of words with highest tf-idf scores
    Given a list of song-line tuple (song_index, line_index),
    returns a list of a word-score tuple, with the word with highest score
    at the head of the list.
"""
def score_lookup(lyrics, scores, songs_lst):
    tfidf_sum = {}
    tfidf_count = {}
    tfidf_scores = []
    for song, line in songs_lst:
        for word_idx in range(len(scores[song][line])):
            word = lyrics[song][line][word_idx]
            score = scores[song][line][word_idx]
            if word.isalpha():
                if tfidf_sum.has_key(word.lower()):
                    tfidf_sum[word.lower()] += score
                    tfidf_count[word.lower()] += 1
                else:
                    tfidf_sum[word.lower()] = score
                    tfidf_count[word.lower()] = 1
    for word, sum_score in tfidf_sum.items():
        tfidf_scores.append((word, sum_score / tfidf_count[word]))

    return sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
