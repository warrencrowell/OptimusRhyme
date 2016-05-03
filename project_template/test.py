import json
from tweetmining import *
from linegen import *
from wordswap import *

nltk.data.path.append('nltk_data/')
search = "trump"

### Get tweet words ###
hashtags = nltk.word_tokenize(search)
TM = TweetMining(method="tf_idf_new")
tweetwords = TM.get_topical_words(hashtags)[0]

### Load corpus ###
if os.path.isfile('lyrics_dataset.json'):
    json_data = open('lyrics_dataset.json').read()
else:
    json_data = open('project_template/lyrics_dataset.json').read()
lyrics = json.loads(json_data)

if os.path.isfile('scores_dataset.json'):
    json_data = open('scores_dataset.json').read()
else:
    json_data = open('project_template/scores_dataset.json').read()
song_tfidf = json.loads(json_data)

### Generate lyrics
output_list = [wordswap(new_random_line(lyrics,song_tfidf),tweetwords)]
for i in range(7):
	line = new_random_line(lyrics,song_tfidf,output_list[-1])
	altered_line = wordswap(line, tweetwords)
	output_list.append(altered_line)
output_list = format_lines(output_list)

for output in output_list:
	print output