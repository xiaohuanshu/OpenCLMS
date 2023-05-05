from .utils import inject_module

# wechat/tasks.py:12
# https://stackoverflow.com/questions/16634773/using-urllib2-for-python3
try:
    import urllib2
except:
    from urllib import request
    inject_module('urllib2', request)
