from django.conf.urls import include, url, patterns
import student, management, teacher

urlpatterns = [

    url(r'^studentlist$', student.studentlist, name='studentlist'),
    url(r'^ajax/studentdata$', student.data, name='getstudentdata'),
    url(r'^ajax/studentselectdata$', student.selectdata, name='getstudentselectdata'),
    url(r'^teacherlist', teacher.teacherlist, name='teacherlist'),
    url(r'^ajax/teacherdata$', teacher.data, name='getteacherdata'),
    url(r'^classlist', management.classlist, name='classlist'),
    url(r'^ajax/classdata', management.classdata, name='getclassdata'),
    url(r'^majorlist', management.majorlist, name='majorlist'),
    url(r'^ajax/majordata', management.majordata, name='getmajordata'),
    url(r'^departmentlist', management.departmentlist, name='departmentlist'),
    url(r'^ajax/departmentdata', management.departmentdata, name='getdepartmentdata'),
    url(r'^administrationlist', management.administrationlist, name='administrationlist'),
    url(r'^ajax/administrationdata', management.administrationdata, name='getadministrationdata'),
    url(r'^classroomlist', management.classroomlist, name='classroomlist'),
    url(r'^ajax/classroomdata', management.classroomdata, name='getclassroomdata'),
    url(r'^schoolterm$', management.schoolterm, name='schoolterm'),
    url(r'^classtime$', management.classtime, name='classtime'),

]
