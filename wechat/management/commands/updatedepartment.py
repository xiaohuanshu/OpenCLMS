# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from wechat.client import wechat_client
from school.models import Class, Department
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        departmentlist = wechat_client.department.get()
        for dep in departmentlist:
            if dep['parentid'] == 1:
                thisdepartmentid = dep['id']
                thisdepartment = Department.objects.get(name=dep['name'])
                cls = Class.objects.filter(department=thisdepartment).all()
                for c in cls:
                    exist = False
                    for d in departmentlist:
                        if c.name == d['name']:
                            exist = True
                            break
                    if not exist:
                        logger.info("[updatedepartment] add department %s" % c.name)
                        wechat_client.department.create(c.name, thisdepartmentid)

        logger.info("[updatedepartment] Successful")
