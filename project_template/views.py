from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from tweetmining import *
from linegen import *
from wordswap import *

# Create your views here.
def index(request):
    output_list = ''
    output=''
    if request.GET.get('search'):
        search = request.GET.get('search')

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

        ### End of our code ###
        paginator = Paginator(output_list, 10)
        page = request.GET.get('page')
        try:
            output = paginator.page(page)
        except PageNotAnInteger:
            output = paginator.page(1)
        except EmptyPage:
            output = paginator.page(paginator.num_pages)
    return render_to_response('project_template/index.html',
                          {'output': output,
                           'magic_url': request.get_full_path(),
                           })
