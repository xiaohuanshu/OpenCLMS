# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from django.shortcuts import render

from models import Teacher
from user_system.auth import permission_required
from django.db.models import Q


@permission_required(permission='school_teacher_view')
def teacherlist(request):
    return render(request, 'teacher_list.html')


@permission_required(permission='school_teacher_view')
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
            teacherdata = teacherdata.filter(teacherid=search)
        else:
            teacherdata = teacherdata.filter(name__icontains=search)

    count = teacherdata.count()
    teacherdata = teacherdata.prefetch_related('department').prefetch_related('administration').select_related('user') \
                      .prefetch_related('user__role').all()[offset: (offset + limit)]

    rows = []
    for p in teacherdata:
        ld = {'teacherid': p.teacherid,
              'name': p.name,
              'sex': (p.sex - 1 and [u'女'] or [u'男'])[0],
              'idnumber': p.idnumber,
              'department': ", ".join(department.name for department in p.department.all()),
              'administration': ", ".join(administration.name for administration in p.administration.all()),
              }
        if p.user:
            ld.update({
                'user_id': p.user_id,
                'username': p.user.username,
                'ip': p.user.ip,
                'iswechat': (p.user.openid and [u'是'] or [u'否'])[0],
                'lastlogintime': p.user.lastlogintime.strftime('%Y-%m-%d %H:%M:%S') if p.user.lastlogintime else '',
                'role': ", ".join(role.name for role in p.user.role.all())
            })
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required(permission='school_teacher_view')
def selectdata(request):
    wd = request.GET['wd']
    limit = 5
    offset = 0
    teacherdata = Teacher.objects.order_by('teacherid')
    count = teacherdata.filter(
        (Q(name__icontains=wd) | Q(teacherid__startswith=wd))
    ).count()
    teacherdata = teacherdata.prefetch_related('department').prefetch_related('administration').filter(
        (Q(name__icontains=wd) | Q(teacherid__startswith=wd))
    )[offset: (offset + limit)]

    rows = []
    for p in teacherdata:
        ld = {'id': p.teacherid, 'name': p.name, 'sex': (p.sex - 1 and [u'女'] or [u'男'])[0],
              'department': ", ".join(department.name for department in p.department.all()),
              'administration': ", ".join(administration.name for administration in p.administration.all())}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")
