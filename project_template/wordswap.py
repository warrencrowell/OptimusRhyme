import nltk
import random

def replace_random_word(line, candidate_words):
	new_line = list(line)
        nltk.data.path.append('nltk_data/')
	pos = nltk.pos_tag(line)
	noun_idxs = []
	for i in range(len(line)):
		if 'NN' in pos[i][1]:
			noun_idxs.append(i)
	if len(noun_idxs) == 0:
		return line
	else:
		rand_noun_idx = random.choice(noun_idxs)
		new_line[rand_noun_idx] = random.choice(candidate_words)
		return new_line



