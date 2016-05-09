# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse
from models import Teacher, Teachertoadministration, Teachertodepartment
from django.db.models import Q
from django.shortcuts import render_to_response, RequestContext
from rbac.auth import resourcejurisdiction_view_auth


@resourcejurisdiction_view_auth(jurisdiction='view_teacher')
def teacherlist(request):
    return render_to_response('teacher_list.html', {}, context_instance=RequestContext(request))


@resourcejurisdiction_view_auth(jurisdiction='view_teacher')
def data(request):
    order = request.GET['order']
    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    sort = request.GET.get('sort', '')
    if not sort == '':
        if order == "asc":
            teacherdata = Teacher.objects.order_by(sort)
        else:
            teacherdata = Teacher.objects.order_by("-%s" % sort)
    else:
        teacherdata = Teacher.objects.order_by('teacherid')
    administration = request.GET.get('administration', '')
    if not administration == '':
        teacherdata = teacherdata.filter(administration__name=administration)
    department = request.GET.get('department', '')
    if not department == '':
        teacherdata = teacherdata.filter(department__name=department)
    search = request.GET.get('search', '')
    if not search == '':
        if search.isdigit():
            count = teacherdata.filter(teacherid=search).count()
            teacherdata = teacherdata.filter(teacherid=search)[offset: (offset + limit)]
        else:
            count = teacherdata.filter(name__icontains=search).count()
            teacherdata = teacherdata.filter(name__icontains=search)[offset: (offset + limit)]
    else:
        count = teacherdata.count()
        teacherdata = teacherdata.prefetch_related('department').prefetch_related('administration').all()[
                      offset: (offset + limit)]

    rows = []
    for p in teacherdata:
        ld = {'teacherid': p.teacherid, 'name': p.name, 'sex': (p.sex - 1 and [u'女'] or [u'男'])[0],
              'idnumber': p.idnumber, 'department': ", ".join(department.name for department in p.department.all()),
              'administration': ", ".join(administration.name for administration in p.administration.all()),
              'username': (p.user and [p.user.username] or [None])[0]}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")
