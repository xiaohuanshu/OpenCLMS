from django.conf.urls import url
import control
import views

urlpatterns = [

    url(r'^qrcheckin/(\d+)$', views.checkin, name='qrcheckin'),
    url(r'^ck/([^/]+)$', control.ck, name='qrck'),
    url(r'^ajax/getqrstr/(\d+)$', control.getqrstr, name='getqrstr'),
    url(r'^ajax/getcheckinnowdata/(\d+)$', control.getcheckinnowdata, name='getcheckinnowdata'),
    url(r'^ajax/changecheckinstatus/(\d+)$', control.changecheckinstatus, name='changecheckinstatus'),
    url(r'^control/startcheckin/(\d+)$', control.startCheckin, name='startcheckin'),
    url(r'^control/stopcheckin/(\d+)$', control.stopCheckin, name='stopcheckin'),
    url(r'^control/clearcheckin/(\d+)$', control.clearcheckin, name='clearcheckin'),

    url(r'^data/course_data/(\d+)$', views.course_data, name='course_data'),
    url(r'^data/student_data/(\d+)$', views.student_data, name='student_data'),
    url(r'^data/teacher_data/(\d+)$', views.teacher_data, name='teacher_data'),
    url(r'^data/personal_data$', views.personaldata, name='personal_data'),
    url(r'^data/lesson_data/(\d+)$', views.lesson_data, name='lesson_data'),

    url(r'^askmanager$', views.askmanager, name='askmanager'),
    url(r'^ajax/getaskdata$', views.askdata, name='getaskdata'),
    url(r'^ajax/addask$', control.addask, name='addask'),
    url(r'^ajax/delask$', control.delask, name='delask'),

    url(r'^jumptolesson_data/(\d+)', views.jumptolesson_data, name='jumptolesson_data'),

]
