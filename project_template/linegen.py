import random

def get_random_line(corpus):
	song = random.choice(corpus)
	line = random.choice(song)
	return line[0]