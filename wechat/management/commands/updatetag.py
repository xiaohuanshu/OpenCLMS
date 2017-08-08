# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from wechat.contact import contact_helper
from school.models import Class, Administration, Major
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        taglist = contact_helper.tag.list()
        taglist = [t['tagname'] for t in taglist]
        if u'学生' not in taglist:
            contact_helper.tag.create(u'学生')
        if u'教师' not in taglist:
            contact_helper.tag.create(u'教师')
        # for schoolyear
        schoolyears = Class.objects.distinct('schoolyear').only('schoolyear')
        for s in schoolyears:
            if str(s.schoolyear) not in taglist:
                contact_helper.tag.create(s.schoolyear)
        # for major
        majors = Major.objects.all()
        for m in majors:
            if m.name not in taglist:
                contact_helper.tag.create(m.name)

        # for administration
        administrations = Administration.objects.all()
        for a in administrations:
            if a.name not in taglist:
                contact_helper.tag.create(a.name)

        logger.info("[updatetag] Successful")
