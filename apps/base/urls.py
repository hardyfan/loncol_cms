# -*- coding: utf-8 -*-
# FileName: urls.py
# Create by Hardy on 2019-12-11
# Description:
from django.urls import path
from .views import *

urlpatterns = [
    path('', hello),
    path('media/', media),
]
