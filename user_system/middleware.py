from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve
from wechat.oauth import getuserinfo
from django.contrib.auth.hashers import check_password
from django.conf import settings
from user_system.models import User
from django.db.models import ObjectDoesNotExist


class UserMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        agent = request.META.get('HTTP_USER_AGENT', None)
        urlname = resolve(request.path)
        urlname = "%s:%s" % (urlname.namespace, urlname.url_name)
        allow_url = ['user:login', 'user:loginProcess', 'user:logout',
                     'user:check_username', 'user:check_email',
                     'wechat:api', 'wechat:oauth', 'user:forgetpassword', 'user:resetpassword',
                     'wechat:wxauth', 'wechat:wechatlogin', 'course:ics']
        wechat_allow_url = ['wechat:oauth', 'wechat:wxauth', 'user:register', 'user:check_username', 'user:check_email',
                            'user:registerProcess']
        if request.session.get('userid', '') == '':
            if 'userid' in request.COOKIES:
                remembercode = request.COOKIES['remembercode']
                if check_password("%s%s" % (
                        request.COOKIES['userid'], settings.SECRET_KEY),
                                  remembercode):
                    try:
                        request.user = User.objects.get(id=request.COOKIES['userid'])
                    except ObjectDoesNotExist:
                        if urlname != 'user:logout':
                            return redirect(reverse('user:logout'))
                        else:
                            return self.get_response(request)
                    request.session['userid'] = request.COOKIES['userid']
                    return self.get_response(request)
            if agent and "MicroMessenger" in agent:
                if urlname in wechat_allow_url:
                    return self.get_response(request)
                if not request.session.get('openid', default=False):
                    return getuserinfo(state=request.get_full_path())

            if urlname not in allow_url:
                request.session['origin'] = request.get_full_path()
                return redirect(reverse('user:login'))
        else:
            try:
                request.user = User.objects.get(id=request.session.get('userid'))
            except ObjectDoesNotExist:
                if urlname != 'user:logout':
                    return redirect(reverse('user:logout'))
                else:
                    return self.get_response(request)
        return self.get_response(request)
