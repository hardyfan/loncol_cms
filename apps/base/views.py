from django.http import HttpResponse


def hello(request):
    return HttpResponse('欢迎使用Django!<a href=/admin>后台管理</a>')
