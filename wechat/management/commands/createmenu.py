# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from wechat.client import wechat_client


class Command(BaseCommand):
    def handle(self, *args, **options):
        wechat_client.menu.create(settings.AGENTID, {
            'button': [
                {
                    'name': u'考勤',
                    'sub_button': [
                        {
                            'type': 'scancode_push',
                            'name': u'签到',
                            'key': '1100'
                        },
                        {
                            'type': 'view',
                            'name': u'个人数据',
                            'url': '%s/checkin/data/personal_data?simpleview=true' % settings.DOMAIN
                        }
                    ]
                },
                {
                    'type': 'view',
                    'name': u'首页',
                    'url': settings.DOMAIN
                },
                {
                    'name': u'其他',
                    'sub_button': [
                        {
                            'type': 'click',
                            'name': u'电脑端地址',
                            'key': '1200'
                        },
                        {
                            'type': 'view',
                            'name': u'导入日历',
                            'url': '%s/course/ics/download?simpleview=true' % settings.DOMAIN
                        }
                    ]
                }
            ]})
        self.stdout.write('Successful!')
