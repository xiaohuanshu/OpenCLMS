# -*- coding: utf-8 -*-
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.conf import settings
import time
from django.views.decorators.csrf import csrf_exempt
from user_system.models import User
from .models import Wechatkeyword
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.enterprise.exceptions import InvalidCorpIdException
from wechatpy.enterprise import parse_message
from wechatpy.replies import TextReply, EmptyReply
from .client import wechat_client
import logging

logger = logging.getLogger(__name__)


# 下面这些变量均假设已由 Request 中提取完毕
@csrf_exempt
def api(request):
    # 从 request 中提取基本信息 (signature, timestamp, nonce, xml)
    signature = request.GET.get('msg_signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    # 解析本次请求的 XML 数据
    crypto = WeChatCrypto(settings.TOKEN, settings.ENCODINGAESKEY, settings.CORPID)
    if request.method == 'GET':
        # 检验合法性
        echo_str = request.GET.get('echostr', '')
        try:
            echo_str = crypto.check_signature(signature, timestamp, nonce, echo_str)
        except InvalidSignatureException:
            # 处理异常情况或忽略
            return HttpResponseBadRequest('Verify Failed')
        return HttpResponse(echo_str, content_type="text/plain")

    try:
        decrypted_xml = crypto.decrypt_message(
            request.body,
            signature,
            timestamp,
            nonce
        )
    except (InvalidCorpIdException, InvalidSignatureException):
        # 处理异常或忽略
        return HttpResponseBadRequest('Failed')
    msg = parse_message(decrypted_xml)
    response = EmptyReply()
    if msg.type == 'text':
        text = msg.content
        if text == 'info':
            userinfo = wechat_client.user.get(msg.source)
            response = TextReply(content=str(userinfo), message=msg)
        else:
            reply = Wechatkeyword.objects.extra(where=['%s SIMILAR TO keyword'], params=[text]).first()
            if reply:
                response = TextReply(content=u'%s' % reply.data, message=msg)
    elif msg.type == 'event':
        if msg.event == 'subscribe':  # 关注事件
            response = EmptyReply()

        elif msg.event == 'unsubscribe':
            logger.info('wechat user %s unsubscribe' % msg.source)
            user = User.objects.get(openid=msg.source)
            user.checkinaccountabnormal = True
            user.save()

        elif msg.event == 'location':
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                user = User.objects.get(openid=msg.source)
            except User.DoesNotExist:
                pass
            else:
                user.latitude = msg.latitude
                user.longitude = msg.longitude
                user.accuracy = msg.precision
                user.lastpositiontime = nowtime
                user.save()

        elif msg.event == 'click':
            if msg.key == '1200':
                response = TextReply(content=u'地址：%s\n学生默认帐号:学号/身份证号\n教师默认帐号:职工号/职工号' % settings.DOMAIN,
                                     message=msg)

    xml = response.render()
    encrypted_xml = crypto.encrypt_message(xml, nonce, timestamp)
    return HttpResponse(encrypted_xml, content_type="application/xml")
