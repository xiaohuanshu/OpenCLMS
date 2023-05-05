# -*- coding: utf-8 -*-
from .models import User
from django.http import HttpResponse
import json
from user_system.auth import permission_required
from user_system.utils import generate_password
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
    newpassword = generate_password(8)
    m = hashlib.md5()
    m.update(newpassword)
    user.password = m.hexdigest()
    user.save()
    return HttpResponse(
        json.dumps({'error': 0, 'message': '已重置为%s' % newpassword}),
        content_type="application/json"
    )
