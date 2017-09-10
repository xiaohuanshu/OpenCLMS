# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from course.tasks import auto_stop_lesson
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('before', type=str)

    def handle(self, *args, **options):
        res = auto_stop_lesson.delay(options['before'])
        self.stdout.write("autostop %d lessons" % res.get())
