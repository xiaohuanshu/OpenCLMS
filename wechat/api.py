# -*- coding: utf-8 -*-
__author__ = 'xiaohuanshu'
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.conf import settings
import time
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from models import Wechatkeyword, Wechatuser


from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.enterprise.exceptions import InvalidCorpIdException
from wechatpy.enterprise import parse_message
from wechatpy.replies import TextReply, EmptyReply
from client import wechat_client

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
            else:
                response = TextReply(content='text reply', message=msg)
    elif msg.type == 'event':
        if msg.event == 'subscribe':  # 关注事件
            response = TextReply(content=u'欢迎关注', message=msg)
            wechatuser, isfirst = Wechatuser.objects.get_or_create(openid=msg.source)

            if isfirst:
                userinfo = wechat_client.user.get(msg.source)
                wechatuser.openid = msg.source
                wechatuser.nickname = userinfo['nickname']
                wechatuser.sex = userinfo['sex']
                wechatuser.city = userinfo['city']
                wechatuser.province = userinfo['province']
                wechatuser.country = userinfo['country']
                wechatuser.headimgurl = userinfo['headimgurl']
                wechatuser.subscribe_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                                          time.localtime(userinfo['subscribe_time']))
                wechatuser.unsubscribe = False
            else:
                wechatuser.unsubscribe = False
            wechatuser.save()

        elif msg.type == 'unsubscribe':
            wechatuser = Wechatuser.objects.get(openid=msg.source)
            wechatuser.unsubscribe = True
            wechatuser.save()

        elif msg.type == 'location':
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            wechatuser = Wechatuser.objects.get(openid=msg.source)
            wechatuser.latitude = msg.latitude
            wechatuser.longitude = msg.longitude
            wechatuser.accuracy = msg.precision
            wechatuser.lastpositiontime = nowtime
            wechatuser.save()

    xml = response.render()
    encrypted_xml = crypto.encrypt_message(xml, nonce, timestamp)
    return HttpResponse(encrypted_xml, content_type="application/xml")


