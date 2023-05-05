from wechatpy.enterprise import WeChatClient
from .storage import DjangoCacheStorage
from django.conf import settings

wechat_client = WeChatClient(
    settings.CORPID,
    settings.APPSECRET,
    session=DjangoCacheStorage()
)
