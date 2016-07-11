try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

# place app url patterns here
import views,management
urlpatterns = [
    url(r'^login$', views.login, name='login'),
    url(r'^loginProcess$', views.loginProcess, name='loginProcess'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^check_username$', views.check_username, name='check_username'),
    url(r'^check_email$', views.check_email, name='check_email'),
    url(r'^registerProcess$', views.registerProcess, name='registerProcess'),
    url(r'^authentication$', views.authentication, name='authentication'),
    url(r'^userlist', management.userlist, name='userlist'),
    url(r'^ajax/userdata', management.userdata, name='getuserdata'),

]