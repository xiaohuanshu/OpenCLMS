# -*- coding: utf-8 -*-
from django.http.response import HttpResponseBadRequest
from .client import wechat_client
from school.models import Student, Teacher
from django.db.models import ObjectDoesNotExist
from django.urls import reverse
from django.core import signing
from django.core.cache import cache
from django.shortcuts import HttpResponseRedirect, render, redirect
from user_system.models import User
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def wxauth(request):
    code = request.GET.get('code')
    if code:
        try:
            user_info = wechat_client.oauth.get_user_info(code)
        except Exception as e:
            return HttpResponseBadRequest(e.errmsg)
        else:
            userid = user_info['UserId']
            userinfo = wechat_client.user.get(userid)
            if userinfo['extattr']['attrs'][0]['name'] == u"学工号":
                thisuserworkid = userinfo['extattr']['attrs'][0]['value']
            else:
                thisuserworkid = userinfo['extattr']['attrs'][1]['value']
            student = None
            teacher = None
            try:
                student = Student.objects.get(studentid=thisuserworkid)
            except ObjectDoesNotExist:
                pass
            try:
                teacher = Teacher.objects.get(teacherid=thisuserworkid)
            except ObjectDoesNotExist:
                pass
            if student is not None:
                user = student.user
                usertype = 'student'
            elif teacher is not None:
                user = teacher.user
                usertype = 'teacher'
            else:
                return HttpResponseBadRequest('Failed')

            if user is not None:
                if user.openid is not None and user.openid != userid:
                    return render(request, 'error.html',
                                  {'message': '认证失败', 'submessage': '此帐号已绑定其他微信号',
                                   'wechatclose': True})
                else:
                    wechat_client.user.verify(userid)
                    user.openid = userid
                    user.save()
                    logger.info('wechat user %s bind to user %s successful' % (userid, user.username))
                    return render(request, 'success.html',
                                  {'message': u'认证成功',
                                   'wechatclose': True})
            else:
                data = {'usertype': usertype, 'workid': thisuserworkid, 'userid': userid}
                return HttpResponseRedirect(reverse('user:register', args=[]) + '?wxauth=%s' % signing.dumps(data))

    else:
        return HttpResponseBadRequest('Failed')


def wechatlogin(request):
    code = request.GET.get('code')
    data = wechat_client.user.get_info(code=code, agent_id=None)
    userid = data['UserId']
    user = User.objects.get(openid=userid)
    request.session['username'] = user.username
    request.session['userid'] = user.id
    origin = request.session.get('origin', '')
    if origin != '':
        del request.session['origin']
        response = HttpResponseRedirect(origin)
    else:
        response = redirect(reverse('home', args=[]))
    return response


def toqywechat(request, target):
    qyurl = {'contact': 'https://work.weixin.qq.com/wework_admin/frame#contacts',
             'send_msg': 'https://work.weixin.qq.com/wework_admin/frame#createMessage'}
    login_url = qyurl[target]
    return HttpResponseRedirect(login_url)
