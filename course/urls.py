from django.urls import re_path
from . import schedule
from . import views
from . import control
from . import ics

app_name = 'course'
urlpatterns = [

    re_path(r'^schedule$', schedule.schedule, name='schedule'),
    re_path(r'^ajax/schedule_data$', schedule.schedule_data, name='schedule_data'),
    re_path(r'^list$', views.list, name='list'),
    re_path(r'^studentcourse/(\d+)$', views.studentcourse, name='studentcourse'),
    re_path(r'^ajax/data$', views.data, name='course_data'),
    re_path(r'^information/(\d+)$', views.information, name='information'),
    re_path(r'^control/startlesson/$', control.startLesson, name='control.startlesson'),
    re_path(r'^control/stoplesson/$', control.stopLesson, name='control.stoplesson'),
    re_path(r'^control/clearlesson/$', control.clearLesson, name='control.clearlesson'),
    re_path(r'^control/sethomeworkscore/$', control.sethomeworkscore, name='control.sethomeworkscore'),
    re_path(r'^control/leavehomeworkcomment/$', control.leavehomeworkcomment, name='control.leavehomeworkcomment'),
    re_path(r'^control/setperformance_score/(\d+)$', control.setperformance_score, name='control.setperformance_score'),
    re_path(r'^control/remind_homework/(\d+)$', control.remind_homework, name='control.remind_homework'),
    re_path(r'^resource/(\d+)$', views.resource, name='resource'),
    re_path(r'^resource/upload$', views.resourceupload, name='resourceupload'),
    re_path(r'^resource/delete$', views.resourcedelete, name='resourcedelete'),
    re_path(r'^course_data/(\d+)$', views.course_data, name='course_data'),
    re_path(r'^homework/(\d+)$', views.homework, name='homework'),
    re_path(r'^homework_commit/(\d+)$', views.get_homework_commit, name='get_homework_commit'),
    re_path(r'^sendmessage/(\d+)$', views.sendmessage, name='sendmessage'),
    re_path(r'^settings/(\d+)', views.settings, name='settings'),

    re_path(r'^codeview', views.codeview, name='codeview'),
    re_path(r'^imgview', views.imgview, name='imgview'),
    re_path(r'^studentcourse_selectdata/(\d+)$', views.studentcourse_selectdata, name='studentcourse_selectdata'),

    re_path(r'^ics/(\d+).ics$', ics.ics, name='ics'),
    re_path(r'^ics/download$', ics.download, name='ics_download'),
    re_path(r'^office_preview$', views.office_preview, name='office_preview'),

    re_path(r'^student_exam/([^/]*)$', views.student_exam, name='student_exam'),
    re_path(r'^personalexam$', views.personalexam, name='personal_exam'),
    re_path(r'^history$', views.course_history, name='course_history'),

]
