import nltk
import random

EXPLICIT_WORDS = ['shit', 'fuck', 'nigg', 'masturb', 'bitch']

def is_explicit(line):
    for word in line:
        for e in EXPLICIT_WORDS:
            if e in word.lower():
                return True
    return False

def get_random_line(corpus, last_line = None):
    while True:
        song = random.choice(corpus)
        while len(song)<1:
            song = random.choice(corpus)
        line = random.choice(song)
        while len(line)<1:
            line = random.choice(song)
        pos = nltk.pos_tag(line)
        noun_found = False
        for i in range(len(line)):
            if 'NN' in pos[i][1]:
                noun_found = True
        if noun_found and not is_explicit(line): 
            if last_line:
                if abs(len(last_line) - len(line)) <= 3:
                    break
            elif len(line) >= 5 and len(line) <= 15:
                break
    return line

def new_random_line(corpus, tf_idf, last_line = None):
    while True:
        song_idx = random.choice(range(len(corpus)))
        song = corpus[song_idx]
        line_idx = random.choice(range(len(song)))
        line = song[line_idx]
        pos = nltk.pos_tag(line)
        noun_found = False
        for i in range(len(line)):
            if 'NN' in pos[i][1]:
                noun_found = True
        if noun_found and not is_explicit(line): 
            if last_line:
                if abs(len(last_line) - len(line)) <= 3:
                    break
            elif len(line) >= 5 and len(line) <= 15:
                break
    return (line, tf_idf[song_idx][line_idx])
