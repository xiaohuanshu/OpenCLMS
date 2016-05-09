# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse
from models import Student
from django.db.models import Q
from django.shortcuts import render_to_response, RequestContext
from rbac.auth import resourcejurisdiction_view_auth


@resourcejurisdiction_view_auth(jurisdiction='view_student')
def studentlist(request):
    return render_to_response('student_list.html', {}, context_instance=RequestContext(request))


@resourcejurisdiction_view_auth(jurisdiction='view_student')
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
            count = studentdata.filter(
                (Q(studentid=search)) | Q(classid__name__icontains=search)
            ).count()
            studentdata = studentdata.select_related('classid').select_related('major').select_related(
                'department').filter(
                (Q(studentid=search)) | Q(classid__name__icontains=search)
            )[offset: (offset + limit)]
        else:
            count = studentdata.filter(
                (Q(name__icontains=search) | Q(studentid__icontains=search)) | Q(classid__name__icontains=search)
            ).count()
            studentdata = studentdata.select_related('classid').select_related('major').select_related(
                'department').filter(
                (Q(name__icontains=search) | Q(studentid__icontains=search)) | Q(classid__name__icontains=search)
            )[offset: (offset + limit)]
    else:
        count = studentdata.count()
        studentdata = studentdata.select_related('classid').select_related('major').select_related(
            'department').all()[offset: (offset + limit)]

    rows = []
    for p in studentdata:
        ld = {'studentid': p.studentid, 'name': p.name, 'sex': (p.sex - 1 and [u'女'] or [u'男'])[0],
              'idnumber': p.idnumber,
              'schoolyear': p.classid.schoolyear, 'class': p.classid.name,
              'username': (p.user and [p.user.username] or [None])[0],
              'major': (p.major and [p.major.name] or [None])[0], 'department': p.department.name}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")
