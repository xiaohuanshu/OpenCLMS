# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.models import Class, Department, Major
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
                name = rs.cell(i, 0).value
                data, created = Class.objects.get_or_create(name=name)
                data.department = Department.objects.get(name=rs.cell(i, 2).value)
                data.major = Major.objects.get(name=rs.cell(i, 1).value)
                data.schoolyear = rs.cell(i, 3).value
                data.save()
            except:
                print "error on class:%s" % name
                count -= 1
        print "successful upgrade %d" % count
