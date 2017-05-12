# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.models import Teacher, Department, Class
from course.models import Course
import xlrd
from progressbar import *
import logging

logger = logging.getLogger(__name__)


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
                data, created = Course.objects.get_or_create(serialnumber=serialnumber,
                                                             schoolterm=options['schoolterm'])
                data.title = rs.cell(i, 1).value
                data.number = rs.cell(i, 2).value
                if rs.cell_type(i, 3) != 0 and rs.cell(i, 3).value != '' and rs.cell(i, 3).value != ' ':
                    data.time = rs.cell(i, 3).value
                if rs.cell_type(i, 4) != 0 and rs.cell(i, 4).value != '' and rs.cell(i, 4).value != ' ':
                    data.location = rs.cell(i, 4).value
                data.department = Department.objects.get(name=rs.cell(i, 5).value)
                data.teachers.add(Teacher.objects.get(teacherid=rs.cell(i, 6).value))
                if rs.cell_type(i, 8) != 0 and rs.cell(i, 8).value != '' and rs.cell(i, 8).value != ' ':
                    teachclass = rs.cell(i, 8).value
                    if not ',' in teachclass:
                        try:
                            data.teachclass = Class.objects.get(name=teachclass.strip())
                        except:
                            pass
                data.save()
                if data.time is not None and data.location is not None:
                    data.simplifytime()
                    data.generatelesson()
            except Exception, e:
                logger.exception("[loadcoursedatafromexcel]error on serialnumber:%s\n%s" % (serialnumber, e))
                count -= 1
        logger.info("[loadcoursedatafromexcel]successful upgrade %d course on %s" % (count, options['excelfile']))
