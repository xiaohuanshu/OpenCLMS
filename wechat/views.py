# -*- coding: utf-8 -*-
from django.http.response import HttpResponseBadRequest
from client import wechat_client
from school.models import Student, Teacher
from django.db.models import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core import signing
from django.shortcuts import HttpResponseRedirect, render_to_response, RequestContext
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
                    return render_to_response('error.html',
                                              {'message': '认证失败', 'submessage': '此帐号已绑定其他微信号',
                                               'wechatclose': True}, context_instance=RequestContext(request))
                else:
                    wechat_client.user.verify(userid)
                    user.openid = userid
                    user.save()
                    logger.info('wechat user %s bind to user %s successful' % (userid, user.username))
                    return render_to_response('success.html',
                                              {'message': u'认证成功',
                                               'wechatclose': True},
                                              context_instance=RequestContext(request))
            else:
                data = {'usertype': usertype, 'workid': thisuserworkid, 'userid': userid}
                return HttpResponseRedirect(reverse('user:register', args=[]) + '?wxauth=%s' % signing.dumps(data))

    else:
        return HttpResponseBadRequest('Failed')


def wechatlogin(request):
    auth_code=request.GET.get('auth_code')
    data = wechat_client.service.get_login_info(auth_code=auth_code,provider_access_token=None)
    #TODO 微信扫码登录
    return HttpResponseBadRequest('Failed')