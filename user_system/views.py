# coding=utf-8
import json
from django.http import HttpResponse
from django.db.models import Q
from models import User, Usertorole, Role
from school.models import Student, Teacher
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, HttpResponseRedirect
from datetime import datetime, timedelta
import time
import hashlib
import re
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from django.conf import settings
from permission import permission_data
from auth import permission_required
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
import uuid
import logging

logger = logging.getLogger(__name__)


def login(request):
    if request.session.get('userid'):
        return redirect(reverse('home', args=[]))
    data = {}
    if "MicroMessenger" not in request.META.get('HTTP_USER_AGENT', ''):
        wxlogin = {'appid': settings.CORPID, 'agentid': settings.AGENTID,
                   'redirect_uri': settings.DOMAIN + reverse('wechat:wechatlogin', args=[])}
        data['wxlogin'] = wxlogin
    if hasattr(settings, "BROWSER_DOWNLOAD_URL"):
        data['browserdownload'] = settings.BROWSER_DOWNLOAD_URL
    return render(request, 'login.html', data)


def register(request):
    return render(request, 'register.html', {})


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

    if username == '' or not re.search('^\w*[a-zA-Z]+\w*$', username) or email == '' or not re.search(
            "^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$",
            email) or password == '' or User.objects.filter(
        Q(email=email) | Q(username=username)).exists():
        return redirect(
            reverse('user:register', args=[]) + u"?error=用户名或邮箱错误")

    m = hashlib.md5()
    m.update(password)
    password = m.hexdigest()
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    user = request.user
    user.username = username
    user.password = password
    user.email = email
    user.lastlogintime = nowtime
    user.ip = request.META['REMOTE_ADDR']

    user.save()
    request.session['userid'] = user.id
    origin = request.session.get('origin', '')
    if origin != '':
        del request.session['origin']
        return HttpResponseRedirect(origin)
    else:
        return redirect(reverse('home', args=[]))


def loginProcess(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    if username == '' or password == '':
        return redirect(reverse('user:login', args=[]))
    else:
        m = hashlib.md5()
        m.update(password)
        password = m.hexdigest()
        try:
            user = User.objects.get(Q(username=username) | Q(academiccode=username) | Q(email=username),
                                    password=password)
            user.lastlogintime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            user.save()
            request.session['userid'] = user.id
            origin = request.session.get('origin', '')
            if not user.username:
                return redirect(reverse('user:register', args=[]))
            if origin != '':
                del request.session['origin']
                response = HttpResponseRedirect(origin)
            else:
                response = redirect(reverse('home', args=[]))
            if request.POST.get('remember', default=False) == "remember-me":
                remembercode = make_password("%d%s" % (user.id, settings.SECRET_KEY), None, 'pbkdf2_sha256')
                response.set_cookie('remembercode', remembercode, None, datetime.now() + timedelta(days=365))
                response.set_cookie('userid', user.id, None, datetime.now() + timedelta(days=365))
            return response
        except ObjectDoesNotExist:
            return redirect(reverse('user:login', args=[]) + u"?error=用户名或密码错误")


def logout(request):
    if request.session.get('userid', default=False):
        del request.session['userid']
    if request.session.get('openid', default=False):
        del request.session['openid']
    response = redirect(reverse('user:login', args=[]))
    if 'remembercode' in request.COOKIES:
        response.delete_cookie('remembercode')
        response.delete_cookie('userid')
    return response


def authentication(request):
    user = request.user
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
                user.sex = student.sex
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
                user.sex = teacher.sex
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
        return render(request, 'authentication.html', {})


@permission_required(permission='user_addpermission')
def add_permission(request):
    if request.META['REQUEST_METHOD'] == 'POST':
        rolename = request.GET.get('role', default=None)
        role = Role.objects.get(name=rolename)
        newpermission = request.POST.getlist('checked[]')
        role.permission = newpermission
        role.save()
        return HttpResponse('{error:0}', content_type="application/json")
    else:
        roledata = Role.objects.all()
        mdata = {}
        mdata['roledata'] = roledata
        rolename = request.GET.get('role', default=None)

        if rolename:
            role = Role.objects.get(name=rolename)
            alreadypermission = role.permission

            def treedata(roots, lastname=''):
                treelist = []
                for root in roots:
                    data = {'text': root['direction'], 'selectable': False, 'name': root['name'], 'permtype': 'res',
                            'nodes': []}
                    if lastname + root['name'] in alreadypermission:
                        data['state'] = {'checked': True}
                    children = root['children']
                    if children is not None:
                        data['nodes'] = treedata(children, lastname + root['name'] + '_')
                    operator = root['operator']
                    if operator is not None:
                        for (offset, op) in enumerate(operator):
                            operatordata = {'text': root['operatordirection'][offset], 'selectable': False, 'name': op,
                                            'permtype': 'operator'}
                            if lastname + root['name'] + '_' + op in alreadypermission:
                                operatordata['state'] = {'checked': True}
                            data['nodes'].append(operatordata)
                    treelist.append(data)
                return treelist

            tree = json.dumps(treedata(permission_data))
            mdata['jurisdictiondata'] = tree
        return render(request, 'addpermission.html', mdata)


@permission_required(permission='user_addrole')
def role(request):
    if request.META['REQUEST_METHOD'] == 'POST':
        rolename = request.GET.get('role', default=None)
        role = Role.objects.get(name=rolename)
        teacherlist = request.POST.getlist('teacherlist[]')
        teacher_users = User.objects.filter(
            pk__in=Teacher.objects.filter(teacherid__in=teacherlist).values_list('user', flat=True))

        old_teacher_user_list = role.user_set.values_list('id', flat=True)
        for tuid in old_teacher_user_list:
            cache.delete('perm_%d_cache' % tuid)
        create_list = []
        for tu in teacher_users:
            cache.delete('perm_%d_cache' % tu.id)
            create_list.append(Usertorole(role=role, user=tu))
            logger.info("add role %s to user %s by user %s" % (rolename, tu.id, request.user.id))
        Usertorole.objects.filter(role=role).delete()
        Usertorole.objects.bulk_create(create_list)
        return HttpResponse('{error:0}', content_type="application/json")
    else:
        newrole = request.GET.get('newrole', default=None)
        if newrole:
            if not Role.objects.filter(name=newrole).exists():
                Role.objects.create(name=newrole)
                return redirect(reverse('user:role', args=[]) + u'?role=%s' % newrole)
        roledata = list(Role.objects.values_list('name', flat=True))
        roledata.remove(u'学生')
        roledata.remove(u'教师')
        mdata = {}
        mdata['roledata'] = roledata
        rolename = request.GET.get('role', default=None)
        if rolename:
            role = Role.objects.get(name=rolename)
            teachers = role.user_set.values('teacher__name', 'teacher__teacherid')
            mdata['teachers'] = teachers
        return render(request, 'role.html', mdata)


def forgetpassword(request):
    email = request.GET.get('email')
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'message': u'找回密码失败', 'submessage': u'没有找到此Email对应的用户'})
    logger.info('user %s forgetpassword' % user.username)
    uuidstr = uuid.uuid1().hex
    cache.set('fp%s' % uuidstr, user.id, 600)
    subject, form_email, to = '【checkinsystem】找回密码邮件', settings.SERVER_EMAIL, email
    text_content = (u'亲爱的%s您好,请点击下面的链接找回密码:\n%s%s\n此链接10分钟内有效,请尽快修改密码。\n'
                    u'如果您没有发起找回密码,请无视此邮件') % (
                       user.username, settings.DOMAIN, reverse('user:resetpassword', args=[uuidstr]))
    html_content = (u'''亲爱的%s您好,<br>请点击下面的链接找回密码:<br><a href="%s%s">%s%s</a><br>
                    此链接10分钟内有效,请尽快修改密码。<br>如果您没有发起找回密码,请无视此邮件''' % (
        user.username, settings.DOMAIN, reverse('user:resetpassword', args=[uuidstr]), settings.DOMAIN,
        reverse('user:resetpassword', args=[uuidstr])))
    msg = EmailMultiAlternatives(subject, text_content, form_email, [to])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    return render(request, 'success.html',
                  {'message': u'邮件发送成功', 'submessage': u'密码找回邮件已发送至%s' % email})


def resetpassword(request, uuidstr):
    userid = cache.get('fp%s' % uuidstr)
    if userid is None:
        return render(request, 'error.html', {'message': u'连接失效', 'submessage': u'连接无效或已经超时'})
    else:
        if request.META['REQUEST_METHOD'] == 'POST':
            password = request.POST.get('password')
            m = hashlib.md5()
            m.update(password)
            password = m.hexdigest()
            User.objects.filter(id=userid).update(password=password)
            cache.delete('fp%s' % uuidstr)
            logger.info('userid %d reset password by email' % userid)
            return render(request, 'success.html', {'message': u'重置成功', 'submessage': u'密码重置成功',
                                                    'jumpurl': reverse('user:login', args=[])})
        else:
            return render(request, 'resetpassword.html', {})


def changepassword(request):
    if request.META['REQUEST_METHOD'] == 'POST':
        oldpassword = request.POST.get('oldpassword')
        password = request.POST.get('newpassword')
        m = hashlib.md5()
        m.update(password)
        password = m.hexdigest()
        m = hashlib.md5()
        m.update(oldpassword)
        oldpassword = m.hexdigest()
        if request.user.password == oldpassword:
            request.user.password = password
            request.user.save()
            logger.info('userid %d changed password')
            return render(request, 'success.html', {'message': u'修改成功', 'submessage': u'密码修改成功',
                                                    'jumpurl': reverse('home', args=[])})
        else:
            return redirect(reverse('user:changepassword', args=[]) + u'?error=原密码错误')
    else:
        return render(request, 'changepassword.html', {})
