from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from linegen import *

# Create your views here.
def index(request):
    output_list = ''
    output=''
    if request.GET.get('search'):
        search = request.GET.get('search')
        ##### OUR CODE #####
        json_data = open('project_template/dataset.json')
        dirty_lyrics = json.load(json_data)
        lyrics = []
        for lyric in dirty_lyrics:
            if len(lyric) > 0:
                lyrics.append(lyric)
        output_list = []
        for i in range(8):
            output_list.append(" ".join(get_random_line(lyrics)))
        ####################
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
