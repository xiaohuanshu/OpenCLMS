# -*- coding: utf-8 -*-
import json
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Schoolterm, Classtime, Class, Major, Department, Administration, Classroom
from user_system.auth import permission_required
import logging

logger = logging.getLogger(__name__)


@permission_required(permission='school_schoolterm_view')
def schoolterm(request):
    if (request.META['REQUEST_METHOD'] == 'POST' and request.POST.get('termname', default=False) and
            request.POST.get('termyear', default=False) and request.POST.get('termstartdate', default=False) and
            request.POST.get('termenddate', default=False)):
        if not request.user.has_perm('school_schoolterm_modify'):
            HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
        if request.POST.get('termid', default=False):
            oldterm = Schoolterm.objects.get(id=request.POST.get('termid'))
            oldterm.schoolyear = request.POST.get('termyear')
            oldterm.description = request.POST.get('termname')
            oldterm.startdate = request.POST.get('termstartdate')
            oldterm.enddate = request.POST.get('termenddate')
            oldterm.save()
        else:
            newterm = Schoolterm(schoolyear=request.POST.get('termyear'), description=request.POST.get('termname'),
                                 now=False,
                                 startdate=request.POST.get('termstartdate'), enddate=request.POST.get('termenddate'))
            newterm.save()
        return redirect(reverse('school:schoolterm', args=[]))
    if request.GET.get('changeterm', default=False):
        oldterm = Schoolterm.objects.get(now=True)
        oldterm.now = False
        oldterm.save()
        newterm = Schoolterm.objects.get(id=request.GET.get('changeterm'))
        newterm.now = True
        newterm.save()
        logger.info('term changed to %s' % newterm.description)
        return redirect(reverse('school:schoolterm', args=[]))
    if request.GET.get('deleteterm', default=False):
        oldterm = Schoolterm.objects.get(id=request.GET.get('deleteterm'))
        oldterm.delete()
        logger.info('term %s deleted' % oldterm.description)
        return redirect(reverse('school:schoolterm', args=[]))
    term = Schoolterm.objects.all().order_by('-startdate')
    return render(request, 'schoolterm.html', {'term': term})


@permission_required(permission='school_classtime_view')
def classtime(request):
    if (request.META['REQUEST_METHOD'] == 'POST' and
            request.POST.get('pk', default=False) and
            request.POST.get('name', default=False) and
            request.POST.get('value', default=False)):
        if not request.user.has_perm('school_classtime_modify'):
            HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
        data = Classtime.objects.get(id=request.POST.get('pk'))
        if request.POST.get('name') == 'starttime':
            data.starttime = request.POST.get('value')
            data.save()
        elif request.POST.get('name') == 'endtime':
            data.endtime = request.POST.get('value')
            data.save()
        logger.info('classtime changed')
        return HttpResponse(json.dumps({'status': 'ok'}), content_type="application/json")
    classtimedata = Classtime.objects.all().order_by('id')
    return render(request, 'classtime.html', {'classtimedata': classtimedata})


@permission_required(permission='school_class_view')
def classlist(request):
    return render(request, 'class.html')


@permission_required(permission='school_class_view')
def classdata(request):
    order = request.GET['order']
    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    sort = request.GET.get('sort', '')
    if not sort == '':
        if order == "asc":
            classdata = Class.objects.order_by(sort)
        else:
            classdata = Class.objects.order_by("-%s" % sort)
    else:
        classdata = Class.objects.order_by('id')
    schoolyear = request.GET.get('schoolyear', '')
    if not schoolyear == '':
        classdata = classdata.filter(schoolyear=schoolyear)
    major = request.GET.get('major', '')
    if not major == '':
        if major[:1] == '*':
            classdata = classdata.filter(department__name=major[1:])
        else:
            classdata = classdata.filter(major__name=major)
    search = request.GET.get('search', '')
    if not search == '':
        count = classdata.filter(name__icontains=search).count()
        classdata = classdata.select_related('major').select_related('department').filter(name__icontains=search)[
                    offset: (offset + limit)]
    else:
        count = classdata.count()
        classdata = classdata.select_related('major').select_related('department').all()[offset: (offset + limit)]

    rows = []
    for p in classdata:
        ld = {'id': p.id, 'name': p.name,
              'schoolyear': p.schoolyear,
              'major': (p.major and [p.major.name] or [None])[0], 'department': p.department.name}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required(permission='school_major_view')
def majorlist(request):
    return render(request, 'major.html')


@permission_required(permission='school_major_view')
def majordata(request):
    order = request.GET['order']
    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    majordata = Major.objects.order_by('id')
    department = request.GET.get('department', '')
    if not department == '':
        majordata = majordata.filter(department__name=department)
    search = request.GET.get('search', '')
    if not search == '':
        count = majordata.filter(name__icontains=search).count()
        majordata = majordata.select_related('department').filter(name__icontains=search)[
                    offset: (offset + limit)]
    else:
        count = majordata.count()
        majordata = majordata.select_related('department').all()[offset: (offset + limit)]

    rows = []
    for p in majordata:
        ld = {'id': p.id, 'name': p.name, 'department': p.department.name, 'number': p.studentnumber,
              'classamount': p.classamount}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required(permission='school_department_view')
def departmentlist(request):
    return render(request, 'department.html')


@permission_required(permission='school_department_view')
def departmentdata(request):
    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    departmentdata = Department.objects.order_by('id')
    search = request.GET.get('search', '')
    if not search == '':
        count = departmentdata.filter(name__icontains=search).count()
        departmentdata = departmentdata.filter(name__icontains=search)[
                         offset: (offset + limit)]
    else:
        count = departmentdata.count()
        departmentdata = departmentdata.all()[offset: (offset + limit)]

    rows = []
    for p in departmentdata:
        ld = {'id': p.id, 'name': p.name, 'studentnumber': p.studentnumber, 'teachernumber': p.teachernumber,
              'majoramount': p.majoramount}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required(permission='school_administration_view')
def administrationlist(request):
    return render(request, 'administration.html')


@permission_required(permission='school_administration_view')
def administrationdata(request):
    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    administrationdata = Administration.objects.order_by('id')
    search = request.GET.get('search', '')
    if not search == '':
        count = administrationdata.filter(name__icontains=search).count()
        administrationdata = administrationdata.filter(name__icontains=search)[
                             offset: (offset + limit)]
    else:
        count = administrationdata.count()
        administrationdata = administrationdata.all()[offset: (offset + limit)]

    rows = []
    for p in administrationdata:
        ld = {'id': p.id, 'name': p.name, 'teachernumber': p.teachernumber}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required(permission='school_classroom_view')
def classroomlist(request):
    return render(request, 'classroom.html')


@permission_required(permission='school_classroom_view')
def classroomdata(request):
    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    classroomdata = Classroom.objects.order_by('id')
    search = request.GET.get('search', '')
    if not search == '':
        count = classroomdata.filter(location__icontains=search).count()
        classroomdata = classroomdata.filter(location__icontains=search)[
                        offset: (offset + limit)]
    else:
        count = classroomdata.count()
        classroomdata = classroomdata.all()[offset: (offset + limit)]

    rows = []
    for p in classroomdata:
        ld = {'id': p.id, 'name': p.location}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")
