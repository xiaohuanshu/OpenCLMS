# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.models import Student
from course.models import Course, Studentcourse
import xlrd
from django.db.models import ObjectDoesNotExist
from progressbar import *

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('excelfile', type=str)

    def handle(self, *args, **options):
        rb = xlrd.open_workbook(options['excelfile'])
        Studentcourse.objects.all().delete()
        rs = rb.sheets()[0]
        count = 0
        progress = ProgressBar()
        for i in progress(range(rs.nrows)):
            count += 1
            try:
                course = Course.objects.get(serialnumber=rs.cell(i, 0).value)
            except ObjectDoesNotExist:
                count -= 1
                print "error on course not found:%s" % rs.cell(i, 0).value
                continue
            try:
                student = Student.objects.get(studentid=rs.cell(i, 1).value)
            except ObjectDoesNotExist:
                count -= 1
                print "error on student not found:%s" % rs.cell(i, 1).value
                continue
            data = Studentcourse(course=course, student=student)
            data.save()
        print "successful insert %d" % count
