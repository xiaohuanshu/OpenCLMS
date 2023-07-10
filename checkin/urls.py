from django.urls import re_path
from . import control
from . import views
from . import dashboard

app_name = 'checkin'
urlpatterns = [

    re_path(r'^qrcheckin/(\d+)$', views.checkin, name='qrcheckin'),
    re_path(r'^ck/([^/]+)$', control.ck, name='qrck'),
    re_path(r'^ajax/getqrstr/(\d+)$', control.getqrstr, name='getqrstr'),
    re_path(r'^ajax/getcheckinnowdata/(\d+)$', control.getcheckinnowdata, name='getcheckinnowdata'),
    re_path(r'^ajax/changecheckinstatus/(\d+)$', control.changecheckinstatus, name='changecheckinstatus'),
    re_path(r'^get_position$', control.get_position, name='get_position'),
    re_path(r'^control/startcheckin/(\d+)$', control.startCheckin, name='startcheckin'),
    re_path(r'^control/stopcheckin/(\d+)$', control.stopCheckin, name='stopcheckin'),
    re_path(r'^control/clearcheckin/(\d+)$', control.clearcheckin, name='clearcheckin'),
    re_path(r'^control/switch_to_add/(\d+)$', control.switch_to_add, name='switch_to_add'),

    re_path(r'^data/student_data/([^/]*)$', views.student_data, name='student_data'),
    re_path(r'^data/teacher_data/([^/]*)$', views.teacher_data, name='teacher_data'),
    re_path(r'^data/class_data/([^/]*)$', views.class_data, name='class_data'),
    re_path(r'^data/personal_data$', views.personaldata, name='personal_data'),
    re_path(r'^data/lesson_data/(\d+)$', views.lesson_data, name='lesson_data'),

    re_path(r'^askmanager$', views.askmanager, name='askmanager'),
    re_path(r'^ajax/getaskdata$', views.askdata, name='getaskdata'),
    re_path(r'^ajax/addask$', control.addask, name='addask'),
    re_path(r'^ajax/delask$', control.delask, name='delask'),

    re_path(r'^jumptolesson_data/(\d+)', views.jumptolesson_data, name='jumptolesson_data'),

    re_path(r'^dashboard/overview', dashboard.overview, name='dashboard_overview'),
    re_path(r'^dashboard/today$', dashboard.today, name='dashboard_today'),
    re_path(r'^dashboard/today_data', dashboard.today_data, name='dashboard_today_data'),
    re_path(r'^dashboard/week$', dashboard.week, name='dashboard_week'),
    re_path(r'^dashboard/week_data', dashboard.week_data, name='dashboard_week_data'),
    re_path(r'^dashboard/term$', dashboard.term, name='dashboard_term'),
    re_path(r'^dashboard/term_data', dashboard.term_data, name='dashboard_term_data'),
    re_path(r'^dashboard/lesson_data', dashboard.lesson_data, name='dashboard_lesson_data'),
    re_path(r'^dashboard/history', dashboard.history, name='dashboard_history'),

    re_path(r'^checkin_success_test', views.checkin_success_test, name='checkin_success_test'),
    re_path(r'^qrcode$', views.qrcode, name='qrcode'),

]
