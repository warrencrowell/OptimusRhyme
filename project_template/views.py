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
import os

# Create your views here.
def index(request):
    output_list = ''
    output=''
    if request.GET.get('search'):
        nltk.data.path.append('nltk_data/')
        search = request.GET.get('search')
        algorithm = request.GET.get('algorithm') # Either 'prototype' or 'final'

        ### Get tweet words ###
        hashtags = search.split()

        if algorithm == 'prototype':
            TM = TweetMining()
            tweetwords = TM.get_topical_words(hashtags)

            if len(tweetwords) == 0:
                output_list = ['Not enough tweets are associated with the input hashtag(s). Please try again.']
            else:
                ### Load corpus ###
                if os.path.isfile('dataset.json'):
                    json_data = open('dataset.json').read()
                else:
                    json_data = open('project_template/dataset.json').read()
                lyrics = json.loads(json_data)

                ### Generate lyrics
                output_list = [replace_random_word(get_random_line(lyrics),tweetwords)]
                for i in range(7):
                    line = get_random_line(lyrics, output_list[-1])
                    altered_line = replace_random_word(line, tweetwords)
                    output_list.append(altered_line)

                output_list = format_lines(output_list)

        elif algorithm == 'final':
            TM = TweetMining(method = 'tf_idf_new')
            tweetwords, word_frequencies = TM.get_topical_words(hashtags)

            if len(tweetwords) == 0:
                output_list = ['Not enough tweets are associated with the input hashtag(s). Please try again.']
            else:
                ### Load corpus ###
                if os.path.isfile('dataset.json'):
                    json_data = open('dataset.json').read()
                else:
                    json_data = open('project_template/dataset.json').read()
                lyrics = json.loads(json_data)

                ### Generate lyrics
                output_list = [replace_random_word(get_random_line(lyrics),tweetwords)]
                for i in range(7):
                    line = get_random_line(lyrics, output_list[-1])
                    altered_line = replace_random_word(line, tweetwords)
                    output_list.append(altered_line)

                output_list = format_lines(output_list)

                input_hashtags = ', '.join(['#' + h if h[0] != '#' else h for h in hashtags])
                output_title = ['<b>TOP FIVE WORDS FOR ' + input_hashtags + '</b>']
                output_list = output_title + tweetwords[:5] + [''] + output_list

        ### End of our code ###
        paginator = Paginator(output_list, 17)
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
                           'word_cloud_list_1': word_frequencies,
                           })
