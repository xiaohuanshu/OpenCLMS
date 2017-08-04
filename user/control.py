# -*- coding: utf-8 -*-
from models import User
from django.http import HttpResponse
import json
from user.auth import permission_required
import hashlib


@permission_required(permission=['school_student_modify', 'user_modify'])
def unbindwechat(request):
    userid = request.GET.get('userid')
    user = User.objects.get(id=userid)
    user.openid = None
    user.save()
    return HttpResponse(json.dumps({'error': 0, 'message': '解绑成功'}), content_type="application/json")


@permission_required(permission=['school_student_modify', 'user_modify'])
def resetpassword(request):
    userid = request.GET.get('userid')
    user = User.objects.get(id=userid)
    m = hashlib.md5()
    m.update('123456')
    user.password = m.hexdigest()
    user.save()
    return HttpResponse(json.dumps({'error': 0, 'message': '已重置为123456'}), content_type="application/json")
