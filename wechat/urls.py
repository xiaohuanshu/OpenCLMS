'''try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *
'''
# place app url patterns here
from django.conf.urls import url
from . import api
from . import oauth
from . import views

app_name = 'wechat'
urlpatterns = [
    url(r'^api$', api.api, name='api'),
    url(r'^wxauth$', views.wxauth, name='wxauth'),
    url(r'^wechatlogin$', views.wechatlogin, name='wechatlogin'),
    url(r'^toqywechat/([^/]+)$', views.toqywechat, name='toqywechat'),
    url(r'^oauth', oauth.oauth, name='oauth'),
]
