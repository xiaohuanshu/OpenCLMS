# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.models import Student, Class, Department, Major
import xlrd
from django.db.models import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('excelfile', type=str)

    def handle(self, *args, **options):
        rb = xlrd.open_workbook(options['excelfile'])
        rs = rb.sheets()[0]
        count = 0
        students = list(Student.objects.values_list('studentid', flat=True))
        for i in range(rs.nrows):
            try:
                count += 1
                studentid = rs.cell(i, 0).value
                data, created = Student.objects.get_or_create(studentid=studentid)
                data.name = rs.cell(i, 1).value

                if rs.cell_type(i, 2) != 0 and rs.cell(i, 2).value != '' and rs.cell(i, 2).value != ' ':
                    data.idnumber = rs.cell(i, 2).value
                else:
                    data.idnumber = ''
                if rs.cell(i, 3).value == u"男":
                    sex = 1
                else:
                    sex = 2
                data.sex = sex
                if rs.cell_type(i, 4) != 0 and rs.cell(i, 4).value != '' and rs.cell(i, 4).value != ' ':
                    data.classid = Class.objects.get(name=rs.cell(i, 4).value)
                data.department = Department.objects.get(name=rs.cell(i, 5).value)
                data.available = True
                try:
                    data.major = Major.objects.get(name=rs.cell(i, 6).value)
                except ObjectDoesNotExist:
                    data.major = data.classid.major
                data.save()
                try:
                    students.remove(studentid)
                except ValueError:
                    pass
            except Exception as e:
                logger.exception("[loadstudentdatafromexcel]error on studentid:%s\n%s" % (studentid, e))
                count -= 1
        notavailablecount = Student.objects.filter(studentid__in=students).update(available=False)
        logger.info("[loadstudentdatafromexcel]setnotavailable %d student on %s" % (notavailablecount, str(students)))
        logger.info("[loadstudentdatafromexcel]successful upgrade %d student on %s" % (count, options['excelfile']))
