try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

# place app url patterns here
import views
import control

urlpatterns = [
    url(r'^login$', views.login, name='login'),
    url(r'^loginProcess$', views.loginProcess, name='loginProcess'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^check_username$', views.check_username, name='check_username'),
    url(r'^check_email$', views.check_email, name='check_email'),
    url(r'^registerProcess$', views.registerProcess, name='registerProcess'),
    url(r'^authentication$', views.authentication, name='authentication'),
    url(r'^forgetpassword$', views.forgetpassword, name='forgetpassword'),
    url(r'^resetpassword/([^/]+)$', views.resetpassword, name='resetpassword'),

    url(r'^addpermission$', views.add_permission, name='addpermission'),

    url(r'^control/unbindwechat', control.unbindwechat, name='control.unbindwechat'),
    url(r'^control/resetpassword', control.resetpassword, name='control.resetpassword'),
    url(r'^addpermission$', views.add_permission, name='addpermission'),
]
