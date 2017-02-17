# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from wechat.client import wechat_client
from school.models import Class,Administration,Major

class Command(BaseCommand):
    def handle(self, *args, **options):
        taglist = wechat_client.tag.list()
        taglist = [t['tagname'] for t in taglist]
        #for schoolyear
        schoolyears = Class.objects.distinct('schoolyear').only('schoolyear')
        for s in schoolyears:
            print s.schoolyear
            if str(s.schoolyear) not in taglist:
                wechat_client.tag.create(s.schoolyear)
        #for major
        majors = Major.objects.all()
        for m in majors:
            print m.name
            if m.name not in taglist:
                wechat_client.tag.create(m.name)

        #for administration
        administrations = Administration.objects.all()
        for a in administrations:
            print a.name
            if a.name not in taglist:
                wechat_client.tag.create(a.name)


        print 'Successful!'
