from django import template
from wechat.api import getjsapi_ticket, wechat
from django.conf import settings
import uuid, json

register = template.Library()


@register.assignment_tag
def wxconfig(url, jsApiList='closeWindow'):
    get_jsapi_ticket = getjsapi_ticket()
    noncestr = uuid.uuid4().hex
    signature = wechat.generate_jsapi_signature(get_jsapi_ticket['jsapi_ticket_expires_at'], noncestr,
                                                '%s%s' % (settings.DOMAIN, url), get_jsapi_ticket['jsapi_ticket'])
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
        settings.APPID,
        get_jsapi_ticket['jsapi_ticket_expires_at'],
        noncestr,
        signature,
        json.dumps(jsApiList.split(','))
    )
