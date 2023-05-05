from .models import Studentcourse, CourseMessage
from wechat.client import wechat_client
from django.conf import settings


def sendmessagetocoursestudent(course, message):
    studentcourses = Studentcourse.objects.select_related("student__user").filter(course=course).all()
    userid = []
    errorsendstudentnames = []
    for sc in studentcourses:
        if sc.student.user and sc.student.user.openid:
            userid.append(sc.student.user.openid)
        else:
            errorsendstudentnames.append(sc.student.name)
    message = "[%s]\n%s" % (course.title, message)
    wechat_client.message.send_text(agent_id=settings.AGENTID, user_ids=userid, content=message)
    CourseMessage.objects.create(course=course, message=message)
    return errorsendstudentnames
