import random

def get_random_line(corpus):
	song = random.choice(corpus)
	# print "got song"
	line = random.choice(song)
	# print "got line"
	return line[0]