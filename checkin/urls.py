from django.conf.urls import include, url, patterns
import control, views

urlpatterns = [

    url(r'^qrcheckin/(\d+)$', views.checkin, name='qrcheckin'),
    url(r'^ck/([^/]+)$', control.ck, name='qrck'),
    url(r'^ck/$', control.ck, name='ckurl'),
    url(r'^ajax/getqrstr/(\d+)$', control.getqrstr, name='getqrstr'),
    url(r'^ajax/getcheckinnowdata/(\d+)$', control.getcheckinnowdata, name='getcheckinnowdata'),
    url(r'^ajax/changecheckinstatus/(\d+)$', control.changecheckinstatus, name='changecheckinstatus'),
    url(r'^control/startcheckin/(\d+)$', control.startCheckin, name='startcheckin'),
    url(r'^control/stopcheckin/(\d+)$', control.stopCheckin, name='stopcheckin'),


    url(r'^data/course_data/(\d+)$', views.course_data, name='course_data'),
    url(r'^data/student_data/(\d+)$', views.student_data, name='student_data'),
    url(r'^data/lesson_data/(\d+)$', views.lesson_data, name='lesson_data'),

]
