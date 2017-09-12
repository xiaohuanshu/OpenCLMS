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
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from center.views import home

urlpatterns = [
    url(r'^$', home, name='home'),

    url(r'^wechat/', include('wechat.urls', namespace="wechat")),
    url(r'^user/', include('user_system.urls', namespace="user")),
    url(r'^school/', include('school.urls', namespace="school")),
    url(r'^course/', include('course.urls', namespace="course")),
    url(r'^checkin/', include('checkin.urls', namespace="checkin")),
    # url(r'^seat$', 'center.views.seat', name='seat'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
