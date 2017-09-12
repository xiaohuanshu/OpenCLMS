# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from school.models import Student, Teacher
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # for student
        students = Student.objects.filter(user=None).all()
        for s in students:
            s.generateuser()
        # for teacher
        teachers = Teacher.objects.filter(user=None).all()
        for t in teachers:
            t.generateuser()
