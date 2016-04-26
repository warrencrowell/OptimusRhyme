import nltk
import random

def get_random_line(corpus, last_line = None):
    while True:
        song = random.choice(corpus)
        line = random.choice(song)
        pos = nltk.pos_tag(line)
        noun_found = False
        for i in range(len(line)):
            if 'NN' in pos[i][1]:
                noun_found = True
        if noun_found and not True in['nigg' in low_word for low_word in [word.lower() for word in line]]:
            if last_line:
                if abs(len(last_line) - len(line)) <= 3:
                    break
            elif len(line) >= 5 and len(line) <= 15:
                break
    return line