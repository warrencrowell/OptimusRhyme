import nltk
from nltk.corpus import wordnet as wn
import random
import cPickle as pickle
import numpy as np
import os

REMOVE_SYMS = ['[', ']', '(', ')']
MERGE_SYMS = [',', '\'', '!', '.', '?', ':']

if os.path.isfile('pho_dict.p'):
    f = open('pho_dict.p', 'rb')
    pho_dict = pickle.load(f)
    f.close()
else:
    f = open('project_template/pho_dict.p', 'rb')
    pho_dict = pickle.load(f)
    f.close()

if os.path.isfile('is_vowel.p'):
    f = open('is_vowel.p', 'rb')
    is_vowel = pickle.load(f)
    f.close()
else:
    f = open('project_template/is_vowel.p', 'rb')
    is_vowel = pickle.load(f)
    f.close()

def wordswap(line, tweet_words, weights=[0,0,0,0,1,1]):
    new_line = list(line)
    line_pos = nltk.pos_tag(line)
    tweet_pos = nltk.pos_tag([tup[0] for tup in tweet_words])
    swaps = []
    for i in range(len(new_line)):
        if not True in [sym in line[i] for sym in (MERGE_SYMS + REMOVE_SYMS)]:
            for j in range(len(tweet_words)):
                swaps.append((i,j))
    scores = np.zeros((len(swaps),6))

    for i, swap in enumerate(swaps):
        # RHYME SCORES
        rhyme_score = rhyme_quality(pho_dict, line[swap[0]], tweet_words[swap[1]][0])
        if rhyme_score:
            scores[i,0] = rhyme_score
        else:
            scores[i,0] = 0

        # PART OF SPEECH
        if line_pos[swap[0]][1] == tweet_pos[swap[1]][1]:
            scores[i,1] = 1
        elif line_pos[swap[0]][1][0:2] == tweet_pos[swap[1]][1][0:2]:
            scores[i,1] = .5
        else:
            scores[i,1] = 0

        # SYLLABLE COUNTS
        word_syls = num_syllables(pho_dict, line[swap[0]])
        tweet_syls = num_syllables(pho_dict, tweet_words[swap[1]][0])
        if word_syls and tweet_words:
            scores[i,2] = 1/float(abs(word_syls - tweet_syls) + 1)

        # TWEET TFIDF
        scores[i,3] = tweet_words[swap[1]][1]

        # SEMANTIC SIMILARITY
        scores[i,5] = compare_word_similarities(line[swap[0]],tweet_words[swap[1]][0])

    # MAKE_SWAP
    normed_scores = np.divide(scores, np.sum(scores,0) + .00000001)
    weighted_scores = np.dot(normed_scores, np.array([weights]).T)
    best_swap = swaps[np.argmax(weighted_scores[:,0])]
    top_score_inds = np.argsort(weighted_scores[:,0])[::-1]
    for i in top_score_inds:
        lyric_ind, tweet_ind = swaps[i]
        new_word = tweet_words[tweet_ind][0]
        if '\'' in line[lyric_ind] or (lyric_ind < len(line) - 1 and
                                        line[lyric_ind + 1][0] == '\''):
            continue

        if new_word.lower() != line[lyric_ind].lower():
            break

    swap_inds = [i for i in range(len(line)) if line[i] == line[lyric_ind]]
    for i in swap_inds:
        to_swap = new_word.capitalize() if i == 0 else new_word
        new_line[i] = ('<div class="substitution">' +
                               to_swap +
                               '<span class="hovertext">' +
                               line[i] +
                               '</span></div>')
    return new_line

def compare_word_similarities(word1,word2):
    syns1 = wn.synsets(word1)
    if(len(syns1)<1):
        return 0.0
    syns2 = wn.synsets(word2)
    if(len(syns2)<1):
        return 0.0
    try:
        sym = wn.wup_similarity(syns1[0],syns2[0])
        return sym
    except:
        return 0.0

# OLD METHOD
def replace_random_word(line, candidate_words):
    new_line = list(line)
    pos = nltk.pos_tag(line)
    noun_idxs = []
    for i in range(len(line)):
        if 'NN' in pos[i][1]:
            noun_idxs.append(i)
    if len(noun_idxs) == 0:
        return line
    else:
        rand_noun_idx = random.choice(noun_idxs)
        old_noun = new_line[rand_noun_idx]
        new_line[rand_noun_idx] = '<font color=\"green\">' + random.choice(candidate_words) + '</font>'
        new_line.append("|")
        new_line.append('<font color=\"red\">' + old_noun + '</font>')
        return new_line

def remove_punctuation(line):
    for i in range(len(line)):
        if line[i] in REMOVE_SYMS:
            if len(line) > i+1:
                return remove_punctuation(line[:i] + line[i+1:])
            else:
                return line[:i]
    return line

def merge_punctuation(line, start_idx):
    for i in range(start_idx, len(line)):
        if True in [sym in line[i] for sym in MERGE_SYMS]:
            line[i-1] = line[i-1] + line[i]
            if len(line) > i+1:
                return merge_punctuation(line[:i] + line[i+1:], i)
            else:
                return line[:i]
    return line

def format_lines(lines):
    new_lines = list(lines)
    for i in range(len(new_lines)):
        curr_line = new_lines[i]
        curr_line = remove_punctuation(curr_line)
        curr_line = merge_punctuation(curr_line, 0)
        curr_line[0] = curr_line[0][0].upper() + curr_line[0][1:]
        new_lines[i] = " ".join(curr_line)
    return new_lines

def rhyme_quality(pho_dict, word_a, word_b):
    vowel_weight = 3
    if not (word_a.upper() in pho_dict and word_b.upper() in pho_dict):
        return None
    phos_a = pho_dict[word_a.upper()]
    phos_b = pho_dict[word_b.upper()]
    edit_dists = np.zeros((len(phos_a) + 1, len(phos_b) + 1))

    for i in range(1,len(phos_a) + 1):
        if is_vowel[phos_a[i-1]]:
            edit_dists[i,0] = edit_dists[i-1,0] + vowel_weight
        else:
            edit_dists[i,0] = edit_dists[i-1,0] + 1

    for j in range(1,len(phos_b) + 1):
        if is_vowel[phos_b[j-1]]:
            edit_dists[0,j] = edit_dists[0,j-1] + vowel_weight
        else:
            edit_dists[0,j] = edit_dists[0,j-1] + 1

    for i in range(1,len(phos_a) + 1):
        for j in range(1,len(phos_b) + 1):
            if phos_a[i-1] == phos_b[j-1]:
                edit_dists[i,j] = edit_dists[i-1,j-1]
            elif is_vowel[phos_a[i-1]] or is_vowel[phos_b[j-1]]:
                edit_dists[i,j] = min(vowel_weight + edit_dists[i-1,j],
                                      vowel_weight + edit_dists[i,j-1],
                                  2 * vowel_weight + edit_dists[i-1,j-1])
            else:
                edit_dists[i,j] = min(1 + edit_dists[i-1,j],
                                      1 + edit_dists[i,j-1],
                                      2 + edit_dists[i-1,j-1])

    worst_dist = edit_dists[len(phos_a),0] + edit_dists[0,len(phos_b)]
    best_dist = edit_dists[len(phos_a),len(phos_b)]
    return worst_dist / float(best_dist + 1)

def num_syllables(pho_dict, word):
    if not word.upper() in pho_dict:
        return None
    else:
        num_syl = 0
        for pho in pho_dict[word.upper()]:
            if is_vowel[pho]:
                num_syl += 1
        return num_syl
