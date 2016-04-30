import nltk
from nltk import wordnet as wn
import random

REMOVE_SYMS = ['[', ']', '(', ')']
MERGE_SYMS = [',', '\'', '!', '.', '?']

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
