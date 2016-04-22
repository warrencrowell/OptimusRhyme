import json
# from tweetmining import *
from linegen import *

json_data = open('dataset.json').read()
lyrics = json.loads(json_data)

output_list = []
for i in range(8):
	output_list.append(" ".join(get_random_line(lyrics)))

print output_list 