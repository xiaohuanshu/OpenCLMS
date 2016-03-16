from django.conf.urls import include, url, patterns
import student, management, teacher

urlpatterns = [

    url(r'^studentlist$', student.studentlist, name='studentlist'),
    url(r'^ajax/studentdata$', student.data, name='getstudentdata'),
    url(r'^teacherlist', teacher.teacherlist, name='teacherlist'),
    url(r'^ajax/teacherdata$', teacher.data, name='getteacherdata'),
    url(r'^classlist', management.classlist, name='classlist'),
    url(r'^ajax/classdata', management.classdata, name='getclassdata'),
    url(r'^majorlist', management.majorlist, name='majorlist'),
    url(r'^ajax/majordata', management.majordata, name='getmajordata'),
    url(r'^schoolterm$', management.schoolterm, name='schoolterm'),
    url(r'^classtime$', management.classtime, name='classtime'),

]
