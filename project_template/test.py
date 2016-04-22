import json
from tweetmining import *
from linegen import *

### Get tweet words ###
tweetwords = ['Hello', 'World']

### Load corpus ###
json_data = open('dataset.json').read()
lyrics = json.loads(json_data)

### Generate lyrics
output_list = []
for i in range(8):
	line = get_random_line(lyrics)
	altered_line = replace_random_word(line, tweetwords)
	output_list.append(" ".join(altered_line))

print output_list 