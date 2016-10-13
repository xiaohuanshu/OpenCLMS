# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.models import Student
from course.models import Course, Studentcourse
import xlrd


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('excelfile', type=str)

    def handle(self, *args, **options):
        rb = xlrd.open_workbook(options['excelfile'])
        Studentcourse.objects.all().delete()
        rs = rb.sheets()[0]
        count = 0
        for i in range(rs.nrows):
            try:
                count += 1
                course = Course.objects.get(serialnumber=rs.cell(i, 0).value)
                student = Student.objects.get(studentid=rs.cell(i, 1).value)
                data = Studentcourse(course=course, student=student)
                data.save()
            except:
                print "error on row:%d" % i
                count -= 1
        print "successful insert %d" % count
