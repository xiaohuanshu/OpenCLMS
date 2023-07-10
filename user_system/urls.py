from django.urls import re_path

# place app url patterns here
from . import views
from . import control

app_name = 'user_system'
urlpatterns = [
    re_path(r'^login$', views.login, name='login'),
    re_path(r'^loginProcess$', views.loginProcess, name='loginProcess'),
    re_path(r'^logout$', views.logout, name='logout'),
    re_path(r'^register$', views.register, name='register'),
    re_path(r'^check_username$', views.check_username, name='check_username'),
    re_path(r'^check_email$', views.check_email, name='check_email'),
    re_path(r'^check_phone$', views.check_phone, name='check_phone'),
    re_path(r'^registerProcess$', views.registerProcess, name='registerProcess'),
    re_path(r'^authentication$', views.authentication, name='authentication'),
    re_path(r'^forgetpassword$', views.forgetpassword, name='forgetpassword'),
    re_path(r'^resetpassword/([^/]+)$', views.resetpassword, name='resetpassword'),
    re_path(r'^changepassword$', views.changepassword, name='changepassword'),

    re_path(r'^addpermission$', views.add_permission, name='addpermission'),

    re_path(r'^control/unbindwechat', control.unbindwechat, name='control.unbindwechat'),
    re_path(r'^control/resetpassword', control.resetpassword, name='control.resetpassword'),
    re_path(r'^addpermission$', views.add_permission, name='addpermission'),
    re_path(r'^role$', views.role, name='role'),
]
