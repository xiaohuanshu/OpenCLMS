# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from wechat.tasks import update_avatar_from_wechat


class Command(BaseCommand):
    def handle(self, *args, **options):
        res = update_avatar_from_wechat.delay()
        counter = res.get()
        self.stdout.write("update %d users" % counter)
