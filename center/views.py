from django.shortcuts import render_to_response, RequestContext

from course.models import Studentcourse, Lesson, Course
from school.function import getCurrentSchoolYearTerm, getnowlessontime
from school.models import Student, Teacher


# Create your views here.
# @resourcejurisdiction_view_auth(jurisdiction='school')
def home(request):
    userid = request.session.get('userid')
    if request.user.isteacher():
        teacher = Teacher.objects.get(user=userid)
        termcourse = Course.objects.filter(teacher=teacher, schoolterm=getCurrentSchoolYearTerm()['term'])
    else:
        student = Student.objects.get(user=userid)
        # alreadycount = Checkin.objects.filter(studentid=student)
        # alreadycount.query.group_by = ['lessonruntimeid__lessonid__id']
        termcourse = Studentcourse.objects.filter(student=student, course__schoolterm=getCurrentSchoolYearTerm()[
            'term']).values_list('course', flat=True)
        termcourse = Course.objects.filter(id__in=termcourse)

    nowlessontime = getnowlessontime()
    lesson = Lesson.objects.filter(course__in=termcourse, week=nowlessontime['week'])

    return render_to_response('home.html',
                              {'term': getCurrentSchoolYearTerm(), 'alreadycount': 0,
                               'termcourse': termcourse.all(),
                               'weeklesson': lesson.select_related('course').all(),
                               },
                              context_instance=RequestContext(request))


def seat(request):
    return render_to_response('seat.html', {}, context_instance=RequestContext(request))
