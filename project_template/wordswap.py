import nltk
import random

MERGE_BACK_TOKS = [',', 'n\'t', '\'s', '\'re', '\'', '!', '.', '?']

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
		new_line[rand_noun_idx] = random.choice(candidate_words) + '*'
		return new_line


def format_punctuation(line): 
    for i in range(len(line)):
        if line[i] in MERGE_BACK_TOKS:
            line[i-1] = line[i-1] + line[i]
            if len(line) > i+1:
                return format_punctuation(line[:i] + line[i+1:])
            else:
                return line[:i]
    return line

def format_lines(lines):
    new_lines = list(lines)	
    for i in range(len(new_lines)):
        curr_line = new_lines[i]
        curr_line[0] = curr_line[0][0].upper() + curr_line[0][1:]
        curr_line = format_punctuation(curr_line)
        new_lines[i] = " ".join(curr_line)
    return new_lines