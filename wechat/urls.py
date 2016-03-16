'''try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *
'''
# place app url patterns here
from django.conf.urls import url
import api
urlpatterns = [
    url(r'^api$', api.api, name='api'),
    url(r'^oauth', api.oauth, name='oauth'),
]