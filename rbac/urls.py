try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

# place app url patterns here
import views
urlpatterns = [
    url(r'^jurisdiction_setup$', views.jurisdiction_setup, name='jurisdiction_setup'),
    ]