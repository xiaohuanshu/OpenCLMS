# -*- coding: utf-8 -*-
# Create your tasks here
from celery import shared_task
from django.conf import settings
from wechat.client import wechat_client
from user_system.models import User
from school.models import Student
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import urllib2
import logging
import datetime

logger = logging.getLogger(__name__)


@shared_task(name='update_avatar_from_wechat')
def update_avatar_from_wechat():
    counter = 0
    users = User.objects.exclude(openid=None).all()
    for u in users:
        counter += 1
        userinfo = wechat_client.user.get(u.openid)
        avatar_url = userinfo['avatar']
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib2.urlopen(avatar_url).read())
        img_temp.flush()
        u.avatar.delete()
        u.avatar.save('%s.jpeg' % u.openid, File(img_temp))
    logger.info("[update_avatar_from_wechat]successful update %d avatar" % counter)
    return counter


@shared_task(name='send_birthday_blessing')
def send_birthday_blessing():
    counter = 0
    todate = datetime.datetime.now().strftime('%m%d')
    students = Student.objects.select_related('user').exclude(user__openid=None) \
        .extra(where=['substring("idnumber",11,4) = \'%s\'' % (todate)]).all()
    for s in students:
        counter += 1
        message = u"%s同学，生日快乐哦！祝你有美好的一天~" % s.name
        wechat_client.message.send_text(agent_id=settings.AGENTID, user_ids=[s.user.openid], content=message)
    logger.info("[send_birthday_blessing]successful send %d students" % counter)
    return counter
