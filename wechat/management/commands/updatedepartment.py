# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from wechat.client import wechat_client
from school.models import Class,Department

import json
class Command(BaseCommand):
    def handle(self, *args, **options):
        departmentlist = wechat_client.department.get()
        for dep in departmentlist:
            if dep['parentid']==1:
                thisdepartmentid = dep['id']
                thisdepartment = Department.objects.get(name=dep['name'])
                cls = Class.objects.filter(department=thisdepartment).all()
                for c in cls:
                    exist = False
                    for d in departmentlist:
                        if c.name == d['name']:
                            exist=True
                            break
                    if not exist:
                        print c.name
                        wechat_client.department.create(c.name,thisdepartmentid)

        print 'Successful!'
