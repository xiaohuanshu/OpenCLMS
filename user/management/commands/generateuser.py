# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from user.models import User, Role, Usertorole
from school.models import Student, Teacher
import hashlib
import logging

logger = logging.getLogger(__name__)


def hashpassword(password):
    m = hashlib.md5()
    m.update(password)
    return m.hexdigest()


class Command(BaseCommand):
    def handle(self, *args, **options):
        teacherrole = Role.objects.get(name='教师')
        studentrole = Role.objects.get(name='学生')
        # for student
        students = Student.objects.filter(user=None).all()
        for s in students:
            user = User(academiccode=s.studentid, password=hashpassword(s.idnumber), sex=s.sex)
            user.save()
            Usertorole(user=user, role=studentrole).save()
            s.user = user
            s.save()
        # for teacher
        teachers = Teacher.objects.filter(user=None).all()
        for t in teachers:
            user = User(academiccode=t.teacherid, password=hashpassword(t.teacherid), sex=t.sex)
            user.save()
            Usertorole(user=user, role=teacherrole).save()
            t.user = user
            t.save()
