from django.conf.urls import url
import control
import views
import dashboard

urlpatterns = [

    url(r'^qrcheckin/(\d+)$', views.checkin, name='qrcheckin'),
    url(r'^ck/([^/]+)$', control.ck, name='qrck'),
    url(r'^ajax/getqrstr/(\d+)$', control.getqrstr, name='getqrstr'),
    url(r'^ajax/getcheckinnowdata/(\d+)$', control.getcheckinnowdata, name='getcheckinnowdata'),
    url(r'^ajax/changecheckinstatus/(\d+)$', control.changecheckinstatus, name='changecheckinstatus'),
    url(r'^get_position$', control.get_position, name='get_position'),
    url(r'^control/startcheckin/(\d+)$', control.startCheckin, name='startcheckin'),
    url(r'^control/stopcheckin/(\d+)$', control.stopCheckin, name='stopcheckin'),
    url(r'^control/clearcheckin/(\d+)$', control.clearcheckin, name='clearcheckin'),

    url(r'^data/student_data/([^/]*)$', views.student_data, name='student_data'),
    url(r'^data/teacher_data/([^/]*)$', views.teacher_data, name='teacher_data'),
    url(r'^data/personal_data$', views.personaldata, name='personal_data'),
    url(r'^data/lesson_data/(\d+)$', views.lesson_data, name='lesson_data'),

    url(r'^askmanager$', views.askmanager, name='askmanager'),
    url(r'^ajax/getaskdata$', views.askdata, name='getaskdata'),
    url(r'^ajax/addask$', control.addask, name='addask'),
    url(r'^ajax/delask$', control.delask, name='delask'),

    url(r'^jumptolesson_data/(\d+)', views.jumptolesson_data, name='jumptolesson_data'),

    url(r'^dashboard/overview', dashboard.overview, name='dashboard_overview'),
    url(r'^dashboard/today$', dashboard.today, name='dashboard_today'),
    url(r'^dashboard/today_data', dashboard.today_data, name='dashboard_today_data'),
    url(r'^dashboard/week$', dashboard.week, name='dashboard_week'),
    url(r'^dashboard/week_data', dashboard.week_data, name='dashboard_week_data'),
    url(r'^dashboard/term$', dashboard.term, name='dashboard_term'),
    url(r'^dashboard/term_data', dashboard.term_data, name='dashboard_term_data'),
    url(r'^dashboard/lesson_data', dashboard.lesson_data, name='dashboard_lesson_data'),

    url(r'^checkin_success_test', views.checkin_success_test, name='checkin_success_test'),
    url(r'^qrcode$', views.qrcode, name='qrcode'),

]
