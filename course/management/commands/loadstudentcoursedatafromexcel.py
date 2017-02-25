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
        parser.add_argument('schoolterm', type=str)
        parser.add_argument('excelfile', type=str)

    def handle(self, *args, **options):
        rb = xlrd.open_workbook(options['excelfile'])
        Studentcourse.objects.filter(course__schoolterm=options['schoolterm']).all().delete()
        rs = rb.sheets()[0]
        count = 0
        coursenotfound = 0
        studentnotfound = 0
        progress = ProgressBar()
        for i in progress(range(rs.nrows)):
            count += 1
            try:
                course = Course.objects.get(serialnumber=rs.cell(i, 0).value)
            except ObjectDoesNotExist:
                count -= 1
                coursenotfound += 1
                # logger.debug("error on course not found:%s" % rs.cell(i, 0).value)
                continue
            try:
                student = Student.objects.get(studentid=rs.cell(i, 1).value)
            except ObjectDoesNotExist:
                count -= 1
                studentnotfound += 1
                # logger.debug("error on student not found:%s" % rs.cell(i, 1).value)
                continue
            data = Studentcourse(course=course, student=student)
            data.save()
        logger.info(
            "[loadstudentcoursedatafromexcel]successful upgrade %d studentcourse with %d course not found and %d student not found on %s" % (
                count, coursenotfound, studentnotfound, options['excelfile']))
