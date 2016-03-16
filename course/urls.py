from django.conf.urls import include, url, patterns
import schedule, views, control

urlpatterns = [

    url(r'^schedule$', schedule.schedule, name='schedule'),
    url(r'^ajax/schedule_data$', schedule.schedule_data, name='schedule_data'),
    url(r'^list$', views.list, name='list'),
    url(r'^ajax/data$', views.data, name='course_data'),
    url(r'^information/(\d+)$', views.information, name='information'),
    url(r'^control/startlesson/$', control.startLesson, name='control.startlesson'),
    url(r'^control/stoplesson/$', control.stopLesson, name='control.stoplesson'),

]
