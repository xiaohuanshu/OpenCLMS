# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from wechat.api import wechat


class Command(BaseCommand):
    def handle(self, *args, **options):
        wechat.create_menu({
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
                            'url': '%s/checkin/data/personal_data' % settings.DOMAIN
                        }
                    ]
                },
                {
                    'type': 'view',
                    'name': u'个人课表',
                    'url': '%s/course/schedule' % settings.DOMAIN
                },
                {
                    'name': u'其他',
                    'sub_button': [
                        {
                            'type': 'click',
                            'name': u'设置',
                            'key': '1200'
                        },
                        {
                            'type': 'view',
                            'name': u'教务系统',
                            'url': 'http://221.218.249.116'
                        }
                    ]
                }
            ]})
        print 'Successful!'
