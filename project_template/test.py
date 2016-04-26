import json
from tweetmining import *
from linegen import *
from wordswap import *

search = "ham sandwich"

### Get tweet words ###
hashtags = nltk.word_tokenize(search)
TM = TweetMining()
tweetwords = TM.get_topical_words(hashtags)

### Load corpus ###
json_data = open('dataset.json').read()
lyrics = json.loads(json_data)

### Generate lyrics
output_list = [get_random_line(lyrics)]
for i in range(8):
	line = get_random_line(lyrics, output_list[-1])
	altered_line = replace_random_word(line, tweetwords)
	output_list.append(altered_line)
output_list = format_lines(output_list)

for output in output_list:
	print output