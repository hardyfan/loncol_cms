import os

from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings


def hello(request):
    return HttpResponse('欢迎使用Django!<a href=/admin>后台管理</a><a href=/media>media</a>')


def media(request):
    media_path = settings.MEDIA_ROOT + '\\editor'
    files = os.listdir(media_path)

    content = {"files": files}
    return render(request, 'base/media.html', content)
