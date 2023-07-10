from django.urls import re_path
from . import student
from . import managementview
from . import teacher

app_name = 'school'
urlpatterns = [

    re_path(r'^studentlist$', student.studentlist, name='studentlist'),
    re_path(r'^ajax/studentdata$', student.data, name='getstudentdata'),
    re_path(r'^ajax/studentselectdata$', student.selectdata, name='getstudentselectdata'),
    re_path(r'^ajax/teacherselectdata$', teacher.selectdata, name='getteacherselectdata'),
    re_path(r'^teacherlist', teacher.teacherlist, name='teacherlist'),
    re_path(r'^ajax/teacherdata$', teacher.data, name='getteacherdata'),
    re_path(r'^classlist', managementview.classlist, name='classlist'),
    re_path(r'^ajax/classdata', managementview.classdata, name='getclassdata'),
    re_path(r'^majorlist', managementview.majorlist, name='majorlist'),
    re_path(r'^ajax/majordata', managementview.majordata, name='getmajordata'),
    re_path(r'^departmentlist', managementview.departmentlist, name='departmentlist'),
    re_path(r'^ajax/departmentdata', managementview.departmentdata, name='getdepartmentdata'),
    re_path(r'^administrationlist', managementview.administrationlist, name='administrationlist'),
    re_path(r'^ajax/administrationdata', managementview.administrationdata, name='getadministrationdata'),
    re_path(r'^classroomlist', managementview.classroomlist, name='classroomlist'),
    re_path(r'^ajax/classroomdata', managementview.classroomdata, name='getclassroomdata'),
    re_path(r'^schoolterm$', managementview.schoolterm, name='schoolterm'),
    re_path(r'^classtime$', managementview.classtime, name='classtime'),

]
