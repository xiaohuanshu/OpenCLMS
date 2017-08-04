# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.models import Teacher, Department, Administration, Teachertoadministration, Teachertodepartment
import xlrd
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('excelfile', type=str)

    def handle(self, *args, **options):
        rb = xlrd.open_workbook(options['excelfile'])
        rs = rb.sheets()[0]
        count = 0
        teachers = list(Teacher.objects.values_list('teacherid', flat=True))
        for i in range(rs.nrows):
            try:
                count += 1
                teacherid = rs.cell(i, 0).value
                data, created = Teacher.objects.get_or_create(teacherid=teacherid)
                data.name = rs.cell(i, 1).value
                data.idnumber = rs.cell(i, 0).value
                if rs.cell(i, 2).value == u"男":
                    sex = 1
                else:
                    sex = 2
                data.sex = sex

                department = Department.objects.get(name=rs.cell(i, 3).value)
                Teachertodepartment.objects.filter(teacher=data).delete()
                Teachertodepartment(teacher=data, department=department).save()
                if rs.cell_type(i, 4) != 0 and rs.cell(i, 4).value != '' and rs.cell(i, 4).value != ' ':
                    administration = Administration.objects.get(name=rs.cell(i, 4).value)
                    Teachertoadministration.objects.filter(teacher=data).delete()
                    Teachertoadministration(teacher=data, administration=administration).save()
                data.available = True
                data.save()
                try:
                    teachers.remove(teacherid)
                except ValueError:
                    pass
            except Exception, e:
                logger.error("[loadteacherdatafromexcel]error on teacherid:%s\n%s" % (teacherid, e))
                count -= 1
        notavailablecount = Teacher.objects.filter(teacherid__in=teachers).update(available=False)
        logger.info("[loadteacherdatafromexcel]setnotavailable %d teachers on %s" % (notavailablecount, str(teachers)))
        logger.info("[loadteacherdatafromexcel]successful upgrade %d teachers on %s" % (count, options['excelfile']))
