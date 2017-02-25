# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from wechat.client import wechat_client
from school.models import Class, Administration, Major
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        taglist = wechat_client.tag.list()
        # taglist = [t['tagname'] for t in taglist]
        # for major
        majors = Major.objects.all()
        for m in majors:
            for t in taglist:
                if m.name == t['tagname']:
                    m.wechattagid = t['tagid']
                    m.save()
                    break

        # for administration
        administrations = Administration.objects.all()
        for a in administrations:
            for t in taglist:
                if a.name == t['tagname']:
                    a.wechattagid = t['tagid']
                    a.save()
                    break

        logger.info("[updatetagid] Successful")
