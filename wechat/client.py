from wechatpy.enterprise import WeChatClient
from wechatpy.session import SessionStorage
from django.core.cache import cache
from django.conf import settings


class CustomStorage(SessionStorage):
    def __init__(self, prefix='wechatpy', *args, **kwargs):
        self.prefix = prefix

    def key_name(self, key):
        return '{0}:{1}'.format(self.prefix, key)

    def get(self, key, default=None):
        value = cache.get(self.key_name(key))
        if value is None:
            return default
        else:
            return value

    def set(self, key, value, ttl=None):
        if value is None:
            return
        cache.set(self.key_name(key), value, ttl)

    def delete(self, key):
        cache.delete(self.key_name(key))


wechat_client = WeChatClient(
    settings.CORPID,
    settings.APPSECRET,
    session=CustomStorage()
)

