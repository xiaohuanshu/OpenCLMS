# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.models import Teacher, Department
from course.models import Course
import xlrd
from progressbar import *

class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument('schoolterm', type=str)
        parser.add_argument('excelfile', type=str)

    def handle(self, *args, **options):
        rb = xlrd.open_workbook(options['excelfile'])
        rs = rb.sheets()[0]
        count = 0
        progress = ProgressBar()
        for i in progress(range(rs.nrows)):
            try:
                count += 1
                serialnumber = rs.cell(i, 0).value
                data, created = Course.objects.get_or_create(serialnumber=serialnumber,schoolterm=options['schoolterm'])
                data.title = rs.cell(i, 1).value
                data.number = rs.cell(i, 2).value
                if rs.cell_type(i, 3) != 0 and rs.cell(i, 3).value != '' and rs.cell(i, 3).value != ' ':
                    data.time = rs.cell(i, 3).value
                if rs.cell_type(i, 4) != 0 and rs.cell(i, 4).value != '' and rs.cell(i, 4).value != ' ':
                    data.location = rs.cell(i, 4).value
                data.department = Department.objects.get(name=rs.cell(i, 5).value)
                data.teacher = Teacher.objects.get(teacherid=rs.cell(i, 6).value)
                if not (data.time is None or data.location is None):
                    data.simplifytime()
                    data.generatelesson()
                data.save()
            except:
                print "error on serialnumber:%s" % serialnumber
                count -= 1
        print "successful upgrade %d" % count
