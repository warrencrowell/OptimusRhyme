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

def consolidate_tfidf(tuple_list):
    tfidf_dict = {}
    for word, score in tuple_list:
        if word in tfidf_dict and tfidf_dict[word] != None:
            tfidf_dict[word] = tfidf_dict[word].append(score)
        elif score and score > 0:
            tfidf_dict[word] = [float(score)]

    result = []
    for word in tfidf_dict:
        if tfidf_dict[word] != None:
            result.append((word, sum(tfidf_dict[word]) / float(len(tfidf_dict[word]))))

    # Adjust tfidf
    max_tfidf = max(result, key = lambda tup: tup[1])[1]
    for i in range(len(result)):
        word, score = result[i]
        result[i] = (word, max(20, 80 * (score / float(max_tfidf))))
    return result

# Create your views here.
def index(request):
    output_list = ''
    output=''
    search=''
    algorithm=''
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
        syllableCountImportance = request.GET.get('syllableCountImportance')
        posImportance = request.GET.get('posImportance')
        hashtagRelevance = request.GET.get('hashtagRelevance')
        lyricRelevance = request.GET.get('lyricRelevance')
        semanticSimilarity = request.GET.get('semanticSimilarity')

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
            word_frequencies, tf = TM.get_topical_words(hashtags)

            if len(word_frequencies) == 0:
                output_list = ['Not enough tweets are associated with the input hashtag(s). Please try again.']
            else:
                ### Generate lyrics
                rand_line = new_random_line(lyrics, song_tfidf)
                lyrics_tfidf = [(rand_line[0][i], rand_line[1][i]) for i in range(len(rand_line[0]))]
                output_list = [wordswap(rand_line, word_frequencies)]
                for i in range(7):
                    line = new_random_line(lyrics,song_tfidf,output_list[-1])
                    lyrics_tfidf.extend([(line[0][i], line[1][i]) for i in range(len(line[0]))])
                    altered_line = wordswap(line, word_frequencies)
                    output_list.append(altered_line)
                output_list = format_lines(output_list)
                lyrics_tfidf = consolidate_tfidf(lyrics_tfidf)

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
                               'word_cloud_list_1': tf,
                               'word_cloud_list_2': lyrics_tfidf,
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
                           'algorithm': algorithm,
                           'rhymeImportance':rhymeImportance,
                           'syllableCountImportance':syllableCountImportance,
                           'posImportance':posImportance,
                           'hashtagRelevance':hashtagRelevance,
                           'lyricRelevance':lyricRelevance,
                           'semanticSimilarity':semanticSimilarity,
                           })
