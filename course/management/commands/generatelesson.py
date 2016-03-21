# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from course.models import Course


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('courseid', type=int)

    def handle(self, *args, **options):
        coursedata = Course.objects.get(id=options['courseid'])
        count = coursedata.generatelesson()
        print 'Successful generate %d lessons' % count
