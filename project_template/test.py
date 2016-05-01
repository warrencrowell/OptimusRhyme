import json
from tweetmining import *
from linegen import *
from wordswap import *


# nltk.data.path.append('nltk_data/')
# search = "ham sandwich"

# ### Get tweet words ###
# hashtags = nltk.word_tokenize(search)
# TM = TweetMining()
# tweetwords = TM.get_topical_words(hashtags)

# ### Load corpus ###
# if os.path.isfile('dataset.json'):
#     json_data = open('dataset.json').read()
# else:
#     json_data = open('project_template/dataset.json').read()
# lyrics = json.loads(json_data)

# ### Generate lyrics
# output_list = [replace_random_word(get_random_line(lyrics),tweetwords)]
# for i in range(7):
# 	line = get_random_line(lyrics, output_list[-1])
# 	altered_line = replace_random_word(line, tweetwords)
# 	output_list.append(altered_line)
# output_list = format_lines(output_list)

# for output in output_list:
# 	print output

nltk.data.path.append('nltk_data/')
search = "dessert"

### Get tweet words ###
hashtags = nltk.word_tokenize(search)
TM = TweetMining(method="tf_idf_new")
tweetwords = TM.get_topical_words(hashtags)

### Load corpus ###
if os.path.isfile('dataset.json'):
    json_data = open('dataset.json').read()
else:
    json_data = open('project_template/dataset.json').read()
lyrics = json.loads(json_data)

### Generate lyrics
output_list = [wordswap(get_random_line(lyrics),tweetwords)]
for i in range(7):
	line = get_random_line(lyrics, output_list[-1])
	altered_line = wordswap(line, tweetwords)
	output_list.append(altered_line)
output_list = format_lines(output_list)

for output in output_list:
	print output