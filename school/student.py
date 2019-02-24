# -*- coding: utf-8 -*-
import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from models import Student
from user_system.auth import permission_required


@permission_required(permission='school_student_view')
def studentlist(request):
    return render(request, 'student_list.html')


@permission_required(permission='school_student_view')
def data(request):
    order = request.GET['order']
    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    # lessondata = Lesson.objects.all()[offset: (offset + limit)]
    sort = request.GET.get('sort', '')
    if not sort == '':
        if order == "asc":
            studentdata = Student.objects.order_by(sort)
        else:
            studentdata = Student.objects.order_by("-%s" % sort)
    else:
        studentdata = Student.objects.order_by('studentid')
    schoolyear = request.GET.get('schoolyear', '')
    if not schoolyear == '':
        studentdata = studentdata.filter(classid__schoolyear=schoolyear)
    major = request.GET.get('major', '')
    if not major == '':
        if major[:1] == '*':
            studentdata = studentdata.filter(department__name=major[1:])
        else:
            studentdata = studentdata.filter(major__name=major)
    search = request.GET.get('search', '')
    if not search == '':
        if search.isdigit():
            studentdata = studentdata.filter(
                (Q(studentid=search)) | Q(classid__name__icontains=search)
            )
        else:
            studentdata = studentdata.filter(
                (Q(name__icontains=search) | Q(studentid__icontains=search)) | Q(classid__name__icontains=search)
            )
    count = studentdata.count()
    studentdata = studentdata.select_related('classid').select_related('major').select_related(
        'department').select_related('user').order_by('studentid').all()[offset: (offset + limit)]

    rows = []
    for p in studentdata:
        ld = {'studentid': p.studentid,
              'name': p.name,
              'sex': (p.sex - 1 and [u'女'] or [u'男'])[0],
              'idnumber': p.idnumber if request.user.has_perm('school_privacy') else u'无权查看',
              'schoolyear': (p.classid and [p.classid.schoolyear] or [None])[0],
              'class': (p.classid and [p.classid.name] or [None])[0],
              'major': (p.major and [p.major.name] or [None])[0],
              'department': p.department.name,
              }
        if p.user:
            ld.update({
                'user_id': p.user_id,
                'username': p.user.username,
                'email': p.user.email if request.user.has_perm('school_privacy') else u'无权查看',
                'phone': p.user.phone if request.user.has_perm('school_privacy') else u'无权查看',
                'ip': p.user.ip,
                'iswechat': (p.user.openid and [u'是'] or [u'否'])[0],
                'lastlogintime': p.user.lastlogintime.strftime('%Y-%m-%d %H:%M:%S') if p.user.lastlogintime else '',
            })
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required(permission='school_student_view')
def selectdata(request):
    wd = request.GET['wd']
    limit = 5
    offset = 0
    # lessondata = Lesson.objects.all()[offset: (offset + limit)]
    studentdata = Student.objects.order_by('studentid')
    count = studentdata.filter(
        (Q(name__icontains=wd) | Q(studentid__startswith=wd))
    ).count()
    studentdata = studentdata.select_related('classid').select_related('major').select_related(
        'department').filter(
        (Q(name__icontains=wd) | Q(studentid__startswith=wd))
    )[offset: (offset + limit)]

    rows = []
    for p in studentdata:
        ld = {'id': p.studentid, 'name': p.name, 'sex': (p.sex - 1 and [u'女'] or [u'男'])[0],
              'class': (p.classid and [p.classid.name] or [None])[0],
              'major': (p.major and [p.major.name] or [None])[0],
              'department': p.department.name}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")
