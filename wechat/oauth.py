from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from user.models import User
from django.http.response import HttpResponse, HttpResponseBadRequest
from client import wechat_client
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@csrf_exempt
def oauth(request):
    code = request.GET.get('code', default=None)
    if code:

        try:
            user_info = wechat_client.oauth.get_user_info(code)
        except Exception as e:
            return HttpResponseBadRequest(e.errmsg)
        else:
            httpresponse = HttpResponseRedirect(request.GET.get('state'))
            request.session['userinfo'] = user_info
            if 'UserId' in user_info:
                userid = user_info['UserId']
                try:
                    user = User.objects.get(openid=userid)
                except ObjectDoesNotExist:
                    return HttpResponseRedirect(reverse('user:wxauth', args=[]) + '?code=%s' % code)
                if not user.verify:
                    request.session['origin'] = request.GET.get('state')
                    httpresponse = redirect(reverse('user:authentication', args=[]))
                request.session['username'] = user.username
                request.session['userid'] = user.id
                remembercode = make_password("%d%s%s" % (user.id, settings.SECRET_KEY, user.username), None,
                                             'pbkdf2_sha256')
                httpresponse.set_cookie('remembercode', remembercode, None, datetime.now() + timedelta(days=365))
                httpresponse.set_cookie('userid', user.id, None, datetime.now() + timedelta(days=365))
                httpresponse.set_cookie('username', user.username, None, datetime.now() + timedelta(days=365))
                return httpresponse
            else:
                return HttpResponseRedirect(settings.WECHATQRCODEURL)
    else:
        return HttpResponseBadRequest('Failed')


def getuserinfo(state='STATE'):
    url = wechat_client.oauth.authorize_url(settings.DOMAIN + reverse('wechat:oauth', args=[]), state)
    return HttpResponseRedirect(url)


def oauth_test(request):
    if request.session.get('openid', default=False):
        pass
    else:
        return getuserinfo(state=request.get_full_path())
