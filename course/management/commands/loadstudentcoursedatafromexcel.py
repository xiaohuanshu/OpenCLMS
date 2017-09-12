# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.models import Student
from course.models import Course, Studentcourse
import xlrd
from django.db.models import ObjectDoesNotExist
from progressbar import *
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('excelfile', type=str)

    def handle(self, *args, **options):
        rb = xlrd.open_workbook(options['excelfile'])
        rs = rb.sheets()[0]
        course_student_map={}
        for i in range(rs.nrows):
            try:
                course_student_map[rs.cell(i, 0).value].add(rs.cell(i, 1).value)
            except KeyError:
                course_student_map[rs.cell(i, 0).value] = set([rs.cell(i, 1).value])
        count = 0
        coursenotfound = 0
        studentnotfound = 0
        progress = ProgressBar()
        for course_serial in progress(course_student_map):
            count+=1
            try:
                course = Course.objects.get(serialnumber=course_serial)
            except ObjectDoesNotExist:
                count -= 1
                coursenotfound += 1
                continue
            if course.disable_sync:
                continue
            Studentcourse.objects.filter(course=course).all().delete()
            student_course_list = []
            for student_id in course_student_map[course_serial]:
                try:
                    student = Student.objects.get(studentid=student_id)
                except ObjectDoesNotExist:
                    studentnotfound += 1
                    continue
                student_course_list.append(Studentcourse(course=course, student=student))
            Studentcourse.objects.bulk_create(student_course_list)
        logger.info(
            "[loadstudentcoursedatafromexcel]successful upgrade %d studentcourse with %d course not found and %d student not found on %s" % (
                count, coursenotfound, studentnotfound, options['excelfile']))
