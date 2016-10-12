# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.models import Student, Class, Department, Major
import xlrd


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('excelfile', type=str)

    def handle(self, *args, **options):
        rb = xlrd.open_workbook(options['excelfile'])
        rs = rb.sheets()[0]
        count = 0
        for i in range(rs.nrows):
            try:
                count += 1
                studentid = rs.cell(i, 0).value
                data, created = Student.objects.get_or_create(studentid=studentid)
                data.name = rs.cell(i, 1).value
                data.idnumber = rs.cell(i, 2).value
                if rs.cell(i, 3).value == u"男":
                    sex = 1
                else:
                    sex = 2
                data.sex = sex
                data.classid = Class.objects.get(name=rs.cell(i, 4).value)
                data.department = Department.objects.get(name=rs.cell(i, 5).value)
                data.major = Major.objects.get(name=rs.cell(i, 6).value)
                data.save()
            except:
                print "error on studentid:%s" % studentid
                count -= 1
        print "successful upgrade %d" % count
