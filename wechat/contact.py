from wechatpy.enterprise import WeChatClient
from storage import DjangoCacheStorage
from django.conf import settings

contact_helper = WeChatClient(
    settings.CORPID,
    settings.CONTACTSECRET,
    session=DjangoCacheStorage()
)
