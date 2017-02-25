# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from wechat.client import wechat_client
from school.models import Class,Department

import json
import logging

logger = logging.getLogger(__name__)
class Command(BaseCommand):
    def handle(self, *args, **options):
        departmentlist = wechat_client.department.get()
        for dep in departmentlist:
            if dep['parentid']==1:
                d = Department.objects.get(name=dep['name'])
                d.wechatdepartmentid=dep['id']
                d.save()
            elif dep['parentid']!=0:
                c = Class.objects.get(name=dep['name'])
                c.wechatdepartmentid=dep['id']
                c.save()

        logger.info("[updatedepartmentid] Successful")
