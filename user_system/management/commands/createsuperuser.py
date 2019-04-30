# -*- coding: utf-8 -*-
"""
Management utility to create superusers.
"""
from __future__ import unicode_literals

import getpass
from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import force_str
from django.utils.six.moves import input
from school.models import Teacher
import hashlib
from user_system.models import User, Role, Usertorole


class Command(BaseCommand):
    help = 'Used to create a superuser.'

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        username = None
        while username is None or username == '':
            username = input("username:")
        email = None
        while email is None or email == '':
            email = input("email:")
        school_id = None
        while school_id is None or school_id == '':
            school_id = input("teacherid:")
        password = None
        while password is None or password == '':
            password = getpass.getpass()
            password2 = getpass.getpass(force_str('Password (again): '))
            if password != password2:
                self.stderr.write("Error: Your passwords didn't match.")
                password = None
                # Don't validate passwords that don't match.
                continue
        teacher = Teacher.objects.create(teacherid=school_id, name=username, idnumber=school_id)
        user = teacher.generateuser()
        print(user)
        m = hashlib.md5()
        m.update(password)
        password = m.hexdigest()
        user.username = username
        user.password = password
        user.email = email
        user.save()
        adminrole = Role.objects.get(name=u'管理员')
        Usertorole.objects.create(user=user, role=adminrole)
        self.stdout.write("Superuser created successfully.")
