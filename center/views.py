from django.shortcuts import render_to_response, RequestContext
from school.function import getCurrentSchoolYearTerm, getnowlessontime
from school.models import Student
from course.models import Studentcourse, Lesson
from rbac.auth import resourcejurisdiction_view_auth

# Create your views here.
#@resourcejurisdiction_view_auth(jurisdiction='school')
def home(request):
    userid = request.session.get('userid')
    student = Student.objects.get(user=userid)
    # alreadycount = Checkin.objects.filter(studentid=student)
    # alreadycount.query.group_by = ['lessonruntimeid__lessonid__id']
    termcourse = Studentcourse.objects.filter(student=student, course__schoolterm=getCurrentSchoolYearTerm()['term'])

    nowlessontime = getnowlessontime()
    lesson = Lesson.objects.filter(course__in=termcourse.values_list('course', flat=True),
                                   day=nowlessontime['day'], week=nowlessontime['week'])

    return render_to_response('home.html',
                              {'term': getCurrentSchoolYearTerm(), 'alreadycount': 0,
                               'termcourse': termcourse.select_related('course').all(),
                               'weeklesson': lesson.select_related('course').all(),
                               },
                              context_instance=RequestContext(request))



def seat(request):
    return render_to_response('seat.html',{},context_instance=RequestContext(request))