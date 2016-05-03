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

# Create your views here.
def index(request):
    output_list = ''
    output=''
    search=''
    algorithm=''
    word_cloud_list_1=''
    rhymeImportance=1
    syllableCountImportance=1
    posImportance=1
    hashtagRelevance=1
    lyricRelevance=1
    semanticSimilarity=1
    if request.GET.get('search'):
        nltk.data.path.append('nltk_data/')
        search = request.GET.get('search')
        algorithm = request.GET.get('algorithm') # Either 'prototype' or 'final'
        rhymeImportance = request.GET.get('rhymeImportance')
        if not rhymeImportance:
            rhymeImportance = 1
        syllableCountImportance = request.GET.get('syllableCountImportance')
        if not syllableCountImportance:
            syllableCountImportance = 1
        posImportance = request.GET.get('posImportance')
        if not posImportance:
            posImportance = 1
        hashtagRelevance = request.GET.get('hashtagRelevance')
        if not hashtagRelevance:
            hashtagRelevance = 1
        lyricRelevance = request.GET.get('lyricRelevance')
        if not lyricRelevance:
            lyricRelevance = 1
        semanticSimilarity = request.GET.get('semanticSimilarity')
        if not semanticSimilarity:
            semanticSimilarity = 1

        ### Get tweet words ###
        hashtags = search.split()

        if algorithm == 'prototype':
            TM = TweetMining()
            tweetwords = TM.get_topical_words(hashtags)

            if len(tweetwords) == 0:
                output_list = ['Not enough tweets are associated with the input hashtag(s). Please try again.']
            else:
                ### Generate lyrics
                output_list = [replace_random_word(get_random_line(lyrics),tweetwords)]
                for i in range(7):
                    line = get_random_line(lyrics, output_list[-1])
                    altered_line = replace_random_word(line, tweetwords)
                    output_list.append(altered_line)

                output_list = format_lines(output_list)
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
                            'search': search,
                            'algorithm': algorithm,
                            'word_cloud_list_1': word_cloud_list_1,
                            'rhymeImportance':rhymeImportance,
                            'syllableCountImportance':syllableCountImportance,
                            'posImportance':posImportance,
                            'hashtagRelevance':hashtagRelevance,
                            'lyricRelevance':lyricRelevance,
                            'semanticSimilarity':semanticSimilarity,
                            })

        elif algorithm == 'final':
            ### Get tweet words ###
            TM = TweetMining(method="tf_idf_new")
            word_frequencies, word_cloud_list_1 = TM.get_topical_words(hashtags)

            if len(word_frequencies) == 0:
                output_list = ['Not enough tweets are associated with the input hashtag(s). Please try again.']
            else:
                ### Generate lyrics
                output_list = [wordswap(new_random_line(lyrics,song_tfidf),word_frequencies)]
                for i in range(7):
                    line = new_random_line(lyrics,song_tfidf,output_list[-1])
                    altered_line = wordswap(line, word_frequencies)
                    output_list.append(altered_line)
                output_list = format_lines(output_list)

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
                               'word_cloud_list_1': word_cloud_list_1,
                               'search': search,
                               'algorithm': algorithm,
                               'rhymeImportance':rhymeImportance,
                               'syllableCountImportance':syllableCountImportance,
                               'posImportance':posImportance,
                               'hashtagRelevance':hashtagRelevance,
                               'lyricRelevance':lyricRelevance,
                               'semanticSimilarity':semanticSimilarity,
                               })

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
                           'search': search,
                           'word_cloud_list_1': word_cloud_list_1,
                           'algorithm': algorithm,
                           'rhymeImportance':rhymeImportance,
                           'syllableCountImportance':syllableCountImportance,
                           'posImportance':posImportance,
                           'hashtagRelevance':hashtagRelevance,
                           'lyricRelevance':lyricRelevance,
                           'semanticSimilarity':semanticSimilarity,
                           })
