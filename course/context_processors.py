from models import Studentcourse, Lesson
from school.function import getnowlessontime


def todaylesson(request):
    if request.session.get('userid', default=False):
        nowlessontime = getnowlessontime()
        userid = request.session.get('userid')
        studentcourse = Studentcourse.objects.filter(student__user=userid).values_list('course', flat=True)
        lesson = Lesson.objects.filter(course__in=studentcourse, term=nowlessontime['term'],
                                              day=nowlessontime['day'], week=nowlessontime['week'])
        data = lesson.select_related('course').all()
        return {'todaylesson': data}
    else:
        return {}
