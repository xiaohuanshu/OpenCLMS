__author__ = 'xiaohuanshu'
from django.shortcuts import render_to_response, RequestContext, redirect
from models import Schoolterm, Classtime, Class, Major, Department
from django.core.urlresolvers import reverse
from django.http import HttpResponse
import json


def schoolterm(request):
    if request.META['REQUEST_METHOD'] == 'POST' and request.POST.get('termname', default=False) and request.POST.get(
            'termyear', default=False) and request.POST.get('termstartdate', default=False) and request.POST.get(
        'termenddate', default=False):
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
        return redirect(reverse('school:schoolterm', args=[]))
    if request.GET.get('deleteterm', default=False):
        oldterm = Schoolterm.objects.get(id=request.GET.get('deleteterm'))
        oldterm.delete()
        return redirect(reverse('school:schoolterm', args=[]))
    term = Schoolterm.objects.all().order_by('-startdate')
    return render_to_response('schoolterm.html', {'term': term}, context_instance=RequestContext(request))


def classtime(request):
    if request.META['REQUEST_METHOD'] == 'POST' and request.POST.get('pk', default=False) and request.POST.get('name',
                                                                                                               default=False) and request.POST.get(
        'value', default=False):
        data = Classtime.objects.get(id=request.POST.get('pk'))
        if request.POST.get('name') == 'starttime':
            data.starttime = request.POST.get('value')
            data.save()
        elif request.POST.get('name') == 'endtime':
            data.endtime = request.POST.get('value')
            data.save()
        return HttpResponse(json.dumps({'status': 'ok'}), content_type="application/json")
    classtimedata = Classtime.objects.all().order_by('id')
    return render_to_response('classtime.html', {'classtimedata': classtimedata},
                              context_instance=RequestContext(request))


def classlist(request):
    return render_to_response('class.html', {}, context_instance=RequestContext(request))


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


def majorlist(request):
    return render_to_response('major.html', {}, context_instance=RequestContext(request))


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
        ld = {'id': p.id, 'name': p.name, 'department': p.department.name, 'number': p.number(),
              'classamount': p.classamount()}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    print data
    return HttpResponse(json.dumps(data), content_type="application/json")
