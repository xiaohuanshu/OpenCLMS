# Create your tasks here
from celery import shared_task

from wechat.client import wechat_client
from user_system.models import User
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import urllib2
import logging

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


