# -*- coding: utf-8 -*-
# Create your tasks here
from celery import shared_task, chain
from school.models import Student, Class, Teacher, Department, Administration, Teachertoadministration, \
    Teachertodepartment, Major, Classroom
from zhengfang.models import Jsxxb, Xsjbxxb, Xsxkb, JxrwbviewXy2, Bjdmb
import logging
import datetime
from django.db.models import ObjectDoesNotExist, Q
from school.function import getCurrentSchoolYearTerm
from course.models import Course, Studentcourse, StudentExam
from wechat.tasks import sync_wechat

logger = logging.getLogger(__name__)


@shared_task(name='sync_zhengfang')
def sync_zhengfang(continuous=None):
    """
    同步步骤：
    班级-》学生-》教师-》课程-》选课->微信
    """
    chain(sync_department.s(),
          sync_student.s(),
          sync_teacher.s(),
          sync_course.s(),
          sync_studentcourse.s(),
          sync_wechat.s(),
          sync_studentexam.s()
          )()


@shared_task(name='sync_department')
def sync_department(continuous=None):
    count = 0
    error_count = 0
    create_class_count = 0
    create_major_count = 0
    create_department_count = 0
    z_classes = Bjdmb.objects.using('zhengfang').filter(Q(sfyx=None) | Q(sfyx='是')).exclude(zcrs=0). \
        extra(select={'zymc': 'select zymc from zydmb where zydmb.zydm = sszydm',
                      'xymc': 'select xymc from xydmb where xydmb.xydm = ssxydm'}).all()

    for z_class in z_classes:
        name = z_class.bjmc
        major_name = z_class.zymc
        department_name = z_class.xymc
        schoolyear = int(z_class.nj)
        count += 1
        try:
            department, created = Department.objects.get_or_create(name=department_name)
            if created:
                create_department_count += 1
            major, created = Major.objects.get_or_create(name=major_name, defaults={'department': department})
            if created:
                create_major_count += 1
            data, created = Class.objects.get_or_create(name=name, defaults={'major': major, 'department': department,
                                                                             'schoolyear': schoolyear})
            if created:
                create_class_count += 1
        except Exception as e:
            logger.exception("[sync_class]error on class name:%s\n%s" % (name, e))
            error_count += 1
    logger.info("[sync_department]Finished count:%d,error:%d,class:%d,major:%d,'department:%d" % (
        count, error_count, create_class_count, create_major_count, create_department_count))


@shared_task(name='sync_student')
def sync_student(continuous=None):
    count = 0
    error_count = 0
    create_count = 0
    students = list(Student.objects.values_list('studentid', flat=True))
    for z_student in Xsjbxxb.objects.filter(xjzt=u"有").using('zhengfang').all():
        studentid = z_student.xh
        try:
            count += 1
            data, created = Student.objects.get_or_create(studentid=studentid)
            if created:
                create_count += 1
            data.name = z_student.xm

            if z_student.sfzh is not None and z_student.sfzh != '' and z_student.sfzh != ' ':
                data.idnumber = z_student.sfzh
            else:
                data.idnumber = ''
            if z_student.xb == u"男":
                sex = 1
            else:
                sex = 2
            data.sex = sex
            if z_student.xzb is not None and z_student.xzb != '' and z_student.xzb != ' ':
                data.classid = Class.objects.get(name=z_student.xzb)
            data.department = Department.objects.get(name=z_student.xy)
            data.available = True
            try:
                data.major = Major.objects.get(name=z_student.zymc)
            except ObjectDoesNotExist:
                if data.classid:
                    data.major = data.classid.major
            data.save()
            try:
                students.remove(studentid)
            except ValueError:
                pass
        except Exception as e:
            logger.exception("[sync_student]error on studentid:%s\n%s" % (studentid, e))
            error_count += 1
    notavailablecount = Student.objects.filter(studentid__in=students).update(available=False)
    logger.info("[sync_student]Finished count:%d,error:%d,create:%d,notavailable:%d" % (
        count, error_count, create_count, notavailablecount))


@shared_task(name='sync_teacher')
def sync_teacher(continuous=None):
    count = 0
    error_count = 0
    create_count = 0
    teachers = list(Teacher.objects.values_list('teacherid', flat=True))
    for z_teacher in Jsxxb.objects.using('zhengfang').all():
        teacherid = z_teacher.zgh
        try:
            count += 1
            data, created = Teacher.objects.get_or_create(teacherid=teacherid)
            if created:
                create_count += 1
            data.name = z_teacher.xm
            data.idnumber = teacherid  # 临时使用职工号代替身份证号
            if z_teacher.xb == u"男":
                sex = 1
            else:
                sex = 2
            data.sex = sex

            department = Department.objects.get(name=z_teacher.bm)
            Teachertodepartment.objects.filter(teacher=data).delete()
            Teachertodepartment(teacher=data, department=department).save()
            if z_teacher.ks is not None and z_teacher.ks != '' and z_teacher.ks != ' ':
                administration, _ = Administration.objects.get_or_create(name=z_teacher.ks)
                Teachertoadministration.objects.filter(teacher=data).delete()
                Teachertoadministration(teacher=data, administration=administration).save()
            data.available = True
            data.save()
            try:
                teachers.remove(teacherid)
            except ValueError:
                pass
        except Exception as e:
            logger.exception("[sync_teacher]error on teacherid:%s\n%s" % (teacherid, e))
            error_count += 1
    notavailablecount = Teacher.objects.filter(teacherid__in=teachers).update(available=False)
    logger.info("[sync_teacher]Finished count:%d,error:%d,create:%d,notavailable:%d" % (
        count, error_count, create_count, notavailablecount))


@shared_task(name='sync_course')
def sync_course(continuous=None):
    skip_skdd = [u'过程考核重修']
    count = 0
    error_count = 0
    create_count = 0
    skip_count = 0
    now_term = getCurrentSchoolYearTerm()['term']
    z_courses = JxrwbviewXy2.objects.using('zhengfang').raw(
        """SELECT kcmc,jszgh,jsxm,SUM (rs) as rs,sksj,skdd,kkxy,xkkh,xkzt,wm_concat (bjmc) as jxb FROM jxrwbview_xy2 
    WHERE xkkh LIKE %s AND (xkzt <> '4' OR xkzt IS NULL)
    GROUP BY SUBSTR (jxjhh, 1, 4),kcdm,kcmc,kcxz,kclb,xf,jszgh,jsxm,zhxs,jkxs,syxs,sjxs,xkkh,sksj,skdd,kkxy,xkkh,xkzt"""
        , ['(' + now_term + ')-%'])

    for z_course in z_courses:
        serialnumber = z_course.xkkh
        try:
            count += 1
            if z_course.sksj is None or z_course.sksj == '' or z_course.sksj == ' ':
                skip_count += 1
                continue
            if z_course.skdd is None or z_course.skdd == '' or z_course.skdd == ' ' or z_course.skdd in skip_skdd:
                skip_count += 1
                continue
            data, created = Course.objects.get_or_create(serialnumber=serialnumber,
                                                         schoolterm=now_term)
            if created:
                create_count += 1
            last_time = data.time
            last_location = data.location

            data.title = z_course.kcmc
            data.number = z_course.rs
            data.time = z_course.sksj
            data.location = z_course.skdd
            data.department = Department.objects.get(name=z_course.kkxy)
            data.teachers.add(Teacher.objects.get(teacherid=z_course.jszgh))
            if z_course.jxb != 0 and z_course.jxb != '' and z_course.jxb != ' ':
                teachclass = z_course.jxb
                if ',' not in teachclass:
                    try:
                        data.teachclass = Class.objects.get(name=teachclass.strip())
                    except:
                        pass
            data.simplifytime()
            data.save()
            if (data.time != last_time or data.location != last_location) and \
                    data.time is not None and data.location is not None:
                data.generatelesson()
        except Exception as e:
            logger.exception("[sync_course]error on serialnumber:%s\n%s" % (serialnumber, e))
            error_count += 1
    logger.info("[sync_course]Finished count:%d,error:%d,create:%d,skip:%d" % (
        count, error_count, create_count, skip_count))


@shared_task(name='sync_studentcourse')
def sync_studentcourse(continuous=None):
    count = 0
    coursenotfound = 0
    studentnotfound = 0
    now_term = getCurrentSchoolYearTerm()['term']

    z_courses = Xsxkb.objects.using('zhengfang').raw(
        "select xkkh,RTRIM(EXTRACT(XMLAGG(XMLELEMENT(\"s\", xh || ',')), '/s/text()').getclobval(),',') as xs from xsxkb where xkkh LIKE %s group by xkkh",
        ['(' + now_term + ')-%'])

    for z_course in z_courses:
        count += 1
        serialnumber = z_course.xkkh
        try:
            course = Course.objects.get(serialnumber=serialnumber)
        except ObjectDoesNotExist:
            coursenotfound += 1
            continue
        if course.disable_sync:
            continue
        exempt_students = course.exempt_students.all()
        student_course_list = []
        old_students = set(Studentcourse.objects.filter(course=course).values_list('student_id', flat=True))
        should_students = set(student_id.strip() for student_id in z_course.xs.read().split(','))
        delete_students = old_students.difference(should_students)
        new_students = should_students.difference(old_students)
        Studentcourse.objects.filter(course=course, student_id__in=delete_students).all().delete()
        for student_id in new_students:
            try:
                student = Student.objects.get(studentid=student_id)
            except ObjectDoesNotExist:
                studentnotfound += 1
                continue
            if student not in exempt_students:
                student_course_list.append(Studentcourse(course=course, student=student))
        Studentcourse.objects.bulk_create(student_course_list)
    logger.info("[sync_studentcourse]Finished count:%d,coursenotfound:%d,studentnotfound:%d" % (
        count, coursenotfound, studentnotfound))


@shared_task(name='sync_studentexam')
def sync_studentexam(continuous=None):
    count = 0
    studentnotfound = 0
    now_term = getCurrentSchoolYearTerm()['term']
    # 考虑到从教务系统同步数据时，存在课程不在考勤系统的情况
    # 所以不在考勤系统中的课程的考试信息，课程都设为Null
    # 为了方便同步，每次同步时，先删除所有为空的课程
    StudentExam.objects.filter(course=None).delete()

    z_exams = Xsxkb.objects.using('zhengfang').filter(xkkh__startswith='(' + now_term + ')-') \
        .exclude(kssj=None).exclude(jsmc=None).all()

    for z_exam in z_exams:
        count += 1
        location, _ = Classroom.objects.get_or_create(location=z_exam.jsmc)
        starttime = datetime.datetime.strptime(
            (u"%s %s" % (z_exam.kssj.split('(')[0], z_exam.kssj[z_exam.kssj.index("(") + 1:z_exam.kssj.index("-")])
             ).encode("utf-8"), "%Y年%m月%d日 %H:%M")
        endtime = datetime.datetime.strptime(
            (u"%s %s" % (z_exam.kssj.split('(')[0], z_exam.kssj[z_exam.kssj.index("-") + 1:z_exam.kssj.index(")")])
             ).encode("utf-8"), "%Y年%m月%d日 %H:%M")

        serialnumber = z_exam.xkkh
        try:
            course = Course.objects.get(serialnumber=serialnumber)
        except ObjectDoesNotExist:
            course = None
        try:
            student = Student.objects.get(studentid=z_exam.xh)
        except ObjectDoesNotExist:
            studentnotfound += 1
            continue

        studentexam, created = StudentExam.objects.get_or_create(course=course, student=student,
                                                                 defaults={
                                                                     'starttime': starttime,
                                                                     'endtime': endtime,
                                                                     'location': location,
                                                                     'seat': z_exam.zwh
                                                                 })
        if not created:
            if starttime != studentexam.starttime or endtime != studentexam.endtime or \
                    location != studentexam.location or z_exam.zwh != studentexam.seat:
                studentexam.starttime = starttime
                studentexam.endtime = endtime
                studentexam.location = location
                studentexam.seat = z_exam.zwh
                studentexam.save()
    logger.info("[sync_studentexam]Finished count:%d,studentnotfound:%d" % (
        count, studentnotfound))
