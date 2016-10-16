__author__ = 'xiaohuanshu'
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve
from wechat.api import oauth_getuserinfo
from django.contrib.auth.hashers import check_password
from django.conf import settings
from user.models import User


class UserMiddleware(object):
    def process_request(self, request):
        agent = request.META.get('HTTP_USER_AGENT', None)
        urlname = resolve(request.path)
        urlname = "%s:%s" % (urlname.namespace, urlname.url_name)
        allow_url = ['user:login', 'user:loginProcess', 'user:register', 'user:logout',
                     'user:check_username', 'user:check_email', 'user:registerProcess',
                     'wechat:api', 'wechat:oauth', 'user:forgetpassword', 'user:resetpassword']
        if request.session.get('username', '') == '':
            if request.COOKIES.has_key('username'):
                remembercode = request.COOKIES['remembercode']
                if check_password("%s%s%s" % (
                        request.COOKIES['userid'], settings.SECRET_KEY, request.COOKIES['username']),
                                  remembercode):
                    request.session['username'] = request.COOKIES['username']
                    request.session['userid'] = request.COOKIES['userid']
                    request.user = User.objects.get(id=request.session.get('userid'))
                    if (not request.user.verify) and urlname != 'user:authentication':
                        return redirect(reverse('user:authentication'))
                    return None
            if agent and "MicroMessenger" in agent:
                if 'wechat:oauth' == urlname:
                    return None
                if not request.session.get('openid', default=False):
                    return oauth_getuserinfo(state=request.get_full_path(), scope=2)

            if urlname not in allow_url:
                request.session['origin'] = request.get_full_path()
                return redirect(reverse('user:login'))
        else:
            request.user = User.objects.get(id=request.session.get('userid'))
            if (not request.user.verify) and urlname != 'user:authentication':
                return redirect(reverse('user:authentication'))
        return None
