from django.conf.urls import url
import schedule
import views
import control
import ics

urlpatterns = [

    url(r'^schedule$', schedule.schedule, name='schedule'),
    url(r'^ajax/schedule_data$', schedule.schedule_data, name='schedule_data'),
    url(r'^list$', views.list, name='list'),
    url(r'^studentcourse/(\d+)$', views.studentcourse, name='studentcourse'),
    url(r'^ajax/data$', views.data, name='course_data'),
    url(r'^information/(\d+)$', views.information, name='information'),
    url(r'^control/startlesson/$', control.startLesson, name='control.startlesson'),
    url(r'^control/stoplesson/$', control.stopLesson, name='control.stoplesson'),
    url(r'^control/clearlesson/$', control.clearLesson, name='control.clearlesson'),
    url(r'^control/sethomeworkscore/$', control.sethomeworkscore, name='control.sethomeworkscore'),
    url(r'^resource/(\d+)$', views.resource, name='resource'),
    url(r'^resource/upload$', views.resourceupload, name='resourceupload'),
    url(r'^resource/delete$', views.resourcedelete, name='resourcedelete'),
    url(r'^homework/(\d+)$', views.homework, name='homework'),
    url(r'^sendmessage/(\d+)$', views.sendmessage, name='sendmessage'),
    url(r'^settings/(\d+)', views.settings, name='settings'),

    url(r'^codeview', views.codeview, name='codeview'),
    url(r'^imgview', views.imgview, name='imgview'),
    url(r'^studentcourse_selectdata/(\d+)$', views.studentcourse_selectdata, name='studentcourse_selectdata'),

    url(r'^ics/(\d+).ics$', ics.ics, name='ics'),

]
