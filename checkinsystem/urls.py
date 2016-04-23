"""checkin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include

urlpatterns = [
    url(r'^$', 'center.views.home', name='home'),

    url(r'^wechat/', include('wechat.urls', namespace="wechat")),
    url(r'^user/', include('user.urls', namespace="user")),
    url(r'^school/', include('school.urls', namespace="school")),
    url(r'^course/', include('course.urls', namespace="course")),
    url(r'^checkin/', include('checkin.urls', namespace="checkin")),
    url(r'^rbac/', include('rbac.urls', namespace="rbac")),
    url(r'^seat$', 'center.views.seat', name='seat'),
]
