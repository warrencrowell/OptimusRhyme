import json
# from tweetmining import *
from linegen import *

json_data = open('project_template/dataset.json').read()
dirty_lyrics = json.loads(json_data)
lyrics = []
for lyric in dirty_lyrics:
	if len(lyric) > 0:
		lyrics.append(lyric)

output_list = []
for i in range(8):
	output_list.append(" ".join(get_random_line(lyrics)))

print output_list
