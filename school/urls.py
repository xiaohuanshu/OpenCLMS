from django.conf.urls import url
import student, managementview, teacher

urlpatterns = [

    url(r'^studentlist$', student.studentlist, name='studentlist'),
    url(r'^ajax/studentdata$', student.data, name='getstudentdata'),
    url(r'^ajax/studentselectdata$', student.selectdata, name='getstudentselectdata'),
    url(r'^ajax/teacherselectdata$', teacher.selectdata, name='getteacherselectdata'),
    url(r'^teacherlist', teacher.teacherlist, name='teacherlist'),
    url(r'^ajax/teacherdata$', teacher.data, name='getteacherdata'),
    url(r'^classlist', managementview.classlist, name='classlist'),
    url(r'^ajax/classdata', managementview.classdata, name='getclassdata'),
    url(r'^majorlist', managementview.majorlist, name='majorlist'),
    url(r'^ajax/majordata', managementview.majordata, name='getmajordata'),
    url(r'^departmentlist', managementview.departmentlist, name='departmentlist'),
    url(r'^ajax/departmentdata', managementview.departmentdata, name='getdepartmentdata'),
    url(r'^administrationlist', managementview.administrationlist, name='administrationlist'),
    url(r'^ajax/administrationdata', managementview.administrationdata, name='getadministrationdata'),
    url(r'^classroomlist', managementview.classroomlist, name='classroomlist'),
    url(r'^ajax/classroomdata', managementview.classroomdata, name='getclassroomdata'),
    url(r'^schoolterm$', managementview.schoolterm, name='schoolterm'),
    url(r'^classtime$', managementview.classtime, name='classtime'),

]
