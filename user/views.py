# coding=utf-8
from django.shortcuts import render
import json
from django.http import HttpResponse
from django.db.models import Q
from models import User, Usertorole, Role
from school.models import Student, Teacher
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response, RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, HttpResponseRedirect
from datetime import datetime, timedelta
import time
import hashlib
import re
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from django.conf import settings


def login(request):
    if request.session.get('username', '') != '':
        return redirect(reverse('home', args=[]))
    return render_to_response('login.html', {}, context_instance=RequestContext(request))


def register(request):
    if request.session.get('username', '') != '':
        return redirect(reverse('home', args=[]))
    return render_to_response('register.html', {}, context_instance=RequestContext(request))


@csrf_exempt
def check_username(request):
    username = request.POST.get('username')
    isAvailable = True
    if User.objects.filter(username=username).exists():
        isAvailable = False
    data = {'valid': isAvailable}
    return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
def check_email(request):
    email = request.POST.get('email')
    isAvailable = True
    if User.objects.filter(email=email).exists():
        isAvailable = False
    data = {'valid': isAvailable}
    return HttpResponse(json.dumps(data), content_type="application/json")


def registerProcess(request):
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    sex = request.POST.get('sex')
    if username == '' or not re.search('^\w*[a-zA-Z]+\w*$', username) or email == '' or not re.search(
            "^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$",
            email) or password == '' or sex == '' or User.objects.filter(
                    Q(email=email) | Q(username=username)).exists():
        return redirect(reverse('user:register', args=[])+ u"?error=用户名或邮箱错误")
    else:
        m = hashlib.md5()
        m.update(password)
        password = m.hexdigest()
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        openid = request.session.get('openid', default=None)
        user = User(username=username, password=password, email=email, sex=sex, registertime=nowtime,
                    lastlogintime=nowtime, ip=request.META['REMOTE_ADDR'], openid=openid)
        user.save()
        request.session['username'] = username
        request.session['userid'] = user.id
        '''
        origin = request.session.get('origin', '')
        if origin != '':
            del request.session['origin']
            return HttpResponseRedirect(origin)
        else:
            return redirect(reverse('home', args=[]))'''
        return redirect(reverse('user:authentication', args=[]))


def loginProcess(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    openid = request.session.get('openid', default=False)
    if username == '' or password == '':
        return redirect(reverse('user:login', args=[]))
    else:
        m = hashlib.md5()
        m.update(password)
        password = m.hexdigest()
        try:
            user = User.objects.get(username=username, password=password)
            if user.openid == None and openid:
                user.openid = openid
                user.save()
            elif user.openid != openid and openid:
                return redirect(reverse('user:login', args=[]) + u"?error=此账户已经绑定其他微信")
            request.session['username'] = username
            request.session['userid'] = user.id
            if not user.verify:
                response = redirect(reverse('user:authentication', args=[]))
            else:
                origin = request.session.get('origin', '')
                if origin != '':
                    del request.session['origin']
                    response = HttpResponseRedirect(origin)
                else:
                    response = redirect(reverse('home', args=[]))
            if request.POST.get('remember', default=False) == "remember-me":
                remembercode = make_password("%d%s%s"%(user.id,settings.SECRET_KEY,username), None, 'pbkdf2_sha256')
                response.set_cookie('remembercode', remembercode, None, datetime.now() + timedelta(days=365))
                response.set_cookie('userid', user.id, None, datetime.now() + timedelta(days=365))
                response.set_cookie('username', username, None, datetime.now() + timedelta(days=365))
            return response
        except ObjectDoesNotExist:
            return redirect(reverse('user:login', args=[]) + u"?error=用户名或密码错误")


def logout(request):
    del request.session['username']
    del request.session['userid']
    if request.session.get('openid', default=False):
        del request.session['openid']
    response = redirect(reverse('user:login', args=[]))
    if request.COOKIES.has_key('remembercode'):
        response.delete_cookie('remembercode')
        response.delete_cookie('userid')
        response.delete_cookie('username')
    return response


def authentication(request):
    user = User.objects.get(id=request.session.get('userid'))
    if user.verify:
        return redirect(reverse('home', args=[]))
    student = None
    teacher = None
    newrole = []
    flag = False
    if request.META['REQUEST_METHOD'] == 'POST' and request.POST.get('fullname', default=False) and request.POST.get(
            'idnumber', default=False) and request.POST.getlist('identity', default=False):
        fullname = request.POST.get('fullname')
        idnumber = request.POST.get('idnumber')

        if '1' in request.POST.getlist('identity') and request.POST.get('studentid', default=False):
            studentid = request.POST.get('studentid')
            try:
                student = Student.objects.get(studentid=studentid, name=fullname, idnumber=idnumber)
                if student.user:
                    return redirect(reverse('user:authentication', args=[]) + u'?error=此学生已经绑定了帐号')
                student.user = user
                flag = True
            except ObjectDoesNotExist:
                return redirect(reverse('user:authentication', args=[]) + u'?error=认证信息有误,没有找到您的学生信息')
            studentrole = Role.objects.get(name='学生')
            newrole.append(Usertorole(user=user, role=studentrole))
        if '2' in request.POST.getlist('identity') and request.POST.get('teacherid', default=False):
            teacherid = request.POST.get('teacherid')
            try:
                teacher = Teacher.objects.get(teacherid=teacherid, name=fullname, idnumber=idnumber)
                if teacher.user:
                    return redirect(reverse('user:authentication', args=[]) + u'?error=此教师已经绑定了帐号')
                teacher.user = user
                flag = True
            except ObjectDoesNotExist:
                return redirect(reverse('user:authentication', args=[]) + u'?error=认证信息有误,没有找到您的教师信息')
            teacherrole = Role.objects.get(name='教师')
            newrole.append(Usertorole(user=user, role=teacherrole))
        if '3' in request.POST.getlist('identity') and request.POST.get('safenumber', default=False):
            safenumber = request.POST.get('safenumber')
            if safenumber != getattr(settings, 'SAFENUMBER'):
                return redirect(reverse('user:authentication', args=[]) + u'?error=安全号码认证失败')
            else:
                adminrole = Role.objects.get(name='管理员')
                newrole.append(Usertorole(user=user, role=adminrole))
                flag = True
        if flag:
            if teacher:
                teacher.save()
            if student:
                student.save()
            for m in newrole:
                m.save()
            user.verify = True
            user.save()
            origin = request.session.get('origin', '')
            if origin != '':
                del request.session['origin']
                return HttpResponseRedirect(origin)
            else:
                return redirect(reverse('home', args=[]))
        else:
            return redirect(reverse('user:authentication', args=[]))
    else:
        return render_to_response('authentication.html', {}, context_instance=RequestContext(request))
