from .utils import inject_module, append_module
from .utils import lowerstrify
import django

# django.core.urlquote, django.core.urlunquote
# course/models.py:15
# https://stackoverflow.com/questions/74875604/cannot-import-name-urlquote-from-django-utils-http
try:
    from django.utils.http import urlquote, urlunquote
except ImportError:
    from urllib.parse import quote, unquote
    inject_module('django.utils.http.urlquote', quote)
    inject_module('django.utils.http.urlunquote', unquote)

# django.core.urlresolvers
# center/templatetags/center_extra.py:3
# https://blog.csdn.net/weixin_43465312/article/details/90142699
try:
    from django.core import urlresolvers
except ImportError:
    from django import urls
    # django.core.urlresolvers = urls
    inject_module('django.core.urlresolvers', urls)

# @django.template.Library.assignment_tag
# center/templatetags/center_extra.py:9
# https://github.com/lazybird/django-carton/issues/3
if not hasattr(django.template.Library, 'assignment_tag'):
    def assignment_tag(self, func=None, takes_context=None, name=None):
        return self.simple_tag(func, takes_context, name)
    django.template.Library.assignment_tag = assignment_tag

# django.conf.urls.url
# checkinsystem/urls.py:16
# https://stackoverflow.com/questions/70319606/importerror-cannot-import-name-url-from-django-conf-urls-after-upgrading-to
try:
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path
    append_module(django.conf.urls, 'url', re_path)

# zhengfang/models.py:51
# error message: NullBooleanField is removed except for support in historical migrations.
#   HINT: Use BooleanField(null=True) instead.
from django.db import models
if models.BooleanField:
    def wrap_NullBooleanField(*args, **kargs):
        return models.BooleanField(*args, **kargs, null=True)
    # just override it
    models.NullBooleanField = wrap_NullBooleanField

# user_system/migrations/0001_initial.py:93
# error message: ValueError: The protocol 'b'IPv4'' is unknown. Supported: ['both', 'ipv4', 'ipv6']
if True:
    orig_GenericIPAddressField = models.GenericIPAddressField
    def wrap_GenericIPAddressField(*args, **kargs):
        if kargs['protocol']:
            kargs['protocol'] = lowerstrify(kargs['protocol'])
        return orig_GenericIPAddressField(*args, **kargs)
    models.GenericIPAddressField = wrap_GenericIPAddressField
