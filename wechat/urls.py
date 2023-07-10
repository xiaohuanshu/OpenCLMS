'''try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *
'''
# place app url patterns here
from django.urls import re_path
from . import api
from . import oauth
from . import views

app_name = 'wechat'
urlpatterns = [
    re_path(r'^api$', api.api, name='api'),
    re_path(r'^wxauth$', views.wxauth, name='wxauth'),
    re_path(r'^wechatlogin$', views.wechatlogin, name='wechatlogin'),
    re_path(r'^toqywechat/([^/]+)$', views.toqywechat, name='toqywechat'),
    re_path(r'^oauth', oauth.oauth, name='oauth'),
]
