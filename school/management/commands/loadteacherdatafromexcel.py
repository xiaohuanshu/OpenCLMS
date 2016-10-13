# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.models import Teacher, Department, Administration, Teachertoadministration, Teachertodepartment
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
                teacherid = rs.cell(i, 0).value
                data, created = Teacher.objects.get_or_create(teacherid=teacherid)
                data.name = rs.cell(i, 1).value
                data.idnumber = rs.cell(i, 2).value
                if rs.cell(i, 3).value == u"男":
                    sex = 1
                else:
                    sex = 2
                data.sex = sex

                department = Department.objects.get(name=rs.cell(i, 3).value)
                Teachertodepartment.objects.filter(teacher=data).delete()
                Teachertodepartment(teacher=data, department=department).save()
                if rs.cell_type(i, 4) != 0 and rs.cell_type(i, 4) != '' and rs.cell_type(i, 4) !=' ':
                    administration = Administration.objects.get(name=rs.cell(i, 4).value)
                    Teachertoadministration.objects.filter(teacher=data).delete()
                    Teachertoadministration(teacher=data, administration=administration).save()
                data.save()
            except:
                print "error on teacherid:%s" % teacherid
                count -= 1
        print "successful upgrade %d" % count
