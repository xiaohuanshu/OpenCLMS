# Create your views here.
import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response, RequestContext

from course.auth import has_course_permission
from models import Course, Lesson, Studentcourse
from school.models import Student
from user.auth import permission_required


def information(request, courseid):
    coursedata = Course.objects.get(id=courseid)
    lessondata = Lesson.objects.filter(course=coursedata).order_by('week', 'day', 'time').all()
    return render_to_response('information.html',
                              {'coursedata': coursedata, 'lessondata': lessondata,
                               'courseperms': has_course_permission(request.user, coursedata)},
                              context_instance=RequestContext(request))


@permission_required(permission='course_viewlist')
def list(request):
    return render_to_response('list.html', {}, context_instance=RequestContext(request))


@permission_required(permission='course_viewlist')
def data(request):
    order = request.GET['order']
    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    # lessondata = Lesson.objects.all()[offset: (offset + limit)]
    sort = request.GET.get('sort', '')
    if not sort == '':
        if order == "asc":
            coursedata = Course.objects.order_by(sort)
        else:
            coursedata = Course.objects.order_by("-%s" % sort)
    else:
        coursedata = Course.objects
    schoolterm = request.GET.get('schoolterm', default=None)
    if schoolterm:
        coursedata = coursedata.filter(schoolterm=schoolterm)
    major = request.GET.get('major', '')
    if not major == '':
        if major[:1] == '*':
            coursedata = coursedata.filter(department__name=major[1:])
        else:
            coursedata = coursedata.filter(major__name=major)
    search = request.GET.get('search', '')
    if not search == '':
        count = coursedata.filter(
            (Q(title__icontains=search) | Q(teacher__name__icontains=search)) | Q(serialnumber=search)
        ).count()
        coursedata = coursedata.select_related('teacher').select_related('major').select_related(
            'department').filter(
            (Q(title__icontains=search) | Q(teacher__name__icontains=search)) | Q(serialnumber=search)
        )[offset: (offset + limit)]
    else:
        count = coursedata.count()
        coursedata = coursedata.select_related('teacher').select_related('major').select_related(
            'department').all()[offset: (offset + limit)]

    rows = []
    for p in coursedata:
        ld = {'id': p.id, 'serialnumber': p.serialnumber, 'title': p.title, 'number': p.number,
              'schoolterm': p.schoolterm, 'time': p.time, 'location': p.location, 'teacher': p.teacher.name,
              'major': (p.major and [p.major.name] or [None])[0], 'department': p.department.name}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")


def studentcourse(request, courseid):
    coursedata = Course.objects.get(id=courseid)
    students = Studentcourse.objects.filter(course=coursedata).select_related('student', 'student__classid',
                                                                              'student__classid__major',
                                                                              'student__classid__department').all()
    return render_to_response('studentcourse.html',
                              {'coursedata': coursedata, 'students': students},
                              context_instance=RequestContext(request))
