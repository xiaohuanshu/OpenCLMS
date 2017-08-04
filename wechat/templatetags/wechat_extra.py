from django import template
from wechat.client import wechat_client
from django.conf import settings
import uuid
import json
import time

register = template.Library()


@register.assignment_tag
def wxconfig(url, jsApiList='closeWindow'):
    ticket = wechat_client.jsapi.get_jsapi_ticket()
    noncestr = uuid.uuid4().hex
    timestamp = int(time.time())
    signature = wechat_client.jsapi.get_jsapi_signature(noncestr, ticket, timestamp,
                                                        '%s%s' % (settings.DOMAIN, url))
    return '''
    <script>
        wx.config({
            debug: %s,
            appId: '%s',
            timestamp: %s,
            nonceStr: '%s',
            signature: '%s',
            jsApiList: %s
        });
    </script>
    ''' % (
        (settings.DEBUG and ['true'] or ['false'])[0],
        settings.CORPID,
        timestamp,
        noncestr,
        signature,
        json.dumps(jsApiList.split(','))
    )
