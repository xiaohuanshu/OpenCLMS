# -*- coding: utf-8 -*-
__author__ = 'xiaohuanshu'
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import (
    TextMessage, VoiceMessage, ImageMessage, VideoMessage, LinkMessage, LocationMessage, EventMessage
)
from django.conf import settings
from django.core.cache import cache
import urllib2, json, time
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from models import Wechatkeyword, Wechatuser
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, HttpResponseRedirect

# 实例化 WechatBasic
access_token = cache.get('access_token')
if not access_token:
    wechat = WechatBasic(
        token=settings.TOKEN,
        appid=settings.APPID,
        appsecret=settings.APPSECRET
    )
    get_access_token = wechat.get_access_token()
    access_token = get_access_token['access_token']
    access_token_expires_at = get_access_token['access_token_expires_at']
    cache.set('access_token', access_token, 7000)
    cache.set('access_token_expires_at', access_token_expires_at, 7000)
else:
    wechat = WechatBasic(
        token=settings.TOKEN,
        appid=settings.APPID,
        appsecret=settings.APPSECRET,
        access_token=access_token,
        access_token_expires_at=cache.get('access_token_expires_at')
    )


# 下面这些变量均假设已由 Request 中提取完毕
@csrf_exempt
def api(request):
    if request.method == 'GET':
        # 检验合法性
        # 从 request 中提取基本信息 (signature, timestamp, nonce, xml)
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')

        if not wechat.check_signature(
                signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponseBadRequest('Verify Failed')

        return HttpResponse(
            request.GET.get('echostr', ''), content_type="text/plain")

    # 解析本次请求的 XML 数据
    try:
        wechat.parse_data(data=request.body)
    except ParseError:
        return HttpResponseBadRequest('Invalid XML Data')

    # 获取解析好的微信请求信息
    message = wechat.get_message()

    response = None
    if isinstance(message, TextMessage):
        text = message.content
        reply = Wechatkeyword.objects.extra(where=['%s SIMILAR TO keyword'], params=[text]).first()
        if reply:
            response = wechat.response_text(content=u'%s' % reply.data)
        else:
            response = wechat.response_text(content=u'文字信息')
        print message.source
    elif isinstance(message, VoiceMessage):
        response = wechat.response_text(content=u'语音信息')
    elif isinstance(message, ImageMessage):
        response = wechat.response_text(content=u'图片信息')
    elif isinstance(message, VideoMessage):
        response = wechat.response_text(content=u'视频信息')
    elif isinstance(message, LinkMessage):
        response = wechat.response_text(content=u'链接信息')
    elif isinstance(message, LocationMessage):
        response = wechat.response_text(content=u'地理位置信息')
    elif isinstance(message, EventMessage):  # 事件信息
        if message.type == 'subscribe':  # 关注事件(包括普通关注事件和扫描二维码造成的关注事件)
            if message.key and message.ticket:  # 如果 key 和 ticket 均不为空，则是扫描二维码造成的关注事件
                response = wechat.response_text(content=u'用户尚未关注时的二维码扫描关注事件')
            else:
                response = wechat.response_text(content=u'普通关注事件')
            wechatuser, isfirst = Wechatuser.objects.get_or_create(openid=message.source)
            if isfirst:
                userinfo = wechat.get_user_info(message.source)
                wechatuser.openid = message.source
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
        elif message.type == 'unsubscribe':
            wechatuser = Wechatuser.objects.get(openid=message.source)
            wechatuser.unsubscribe = True
            wechatuser.save()
        elif message.type == 'scan':
            response = wechat.response_text(content=u'用户已关注时的二维码扫描事件')
        elif message.type == 'location':
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            wechatuser = Wechatuser.objects.get(openid=message.source)
            wechatuser.latitude = message.latitude
            wechatuser.longitude = message.longitude
            wechatuser.accuracy = message.precision
            wechatuser.lastpositiontime = nowtime
            wechatuser.save()
        elif message.type == 'click':
            response = wechat.response_text(content=u'自定义菜单点击事件' + message.key)
        elif message.type == 'view':
            response = wechat.response_text(content=u'自定义菜单跳转链接事件')
        elif message.type == 'templatesendjobfinish':
            response = wechat.response_text(content=u'模板消息事件')

    return HttpResponse(response, content_type="application/xml")


@csrf_exempt
def oauth(request):
    if request.GET.get('code'):
        req = urllib2.Request(
            'https://api.weixin.qq.com/sns/oauth2/access_token?appid=' + settings.APPID + '&secret=' + settings.APPSECRET + '&code=' + request.GET.get(
                'code') + '&grant_type=authorization_code')
        resp = urllib2.urlopen(req)
        content = resp.read()
        response = json.loads(content)
        if response['scope'] == 'snsapi_base':
            request.session['openid'] = response['openid']
            try:
                user = User.objects.get(openid=response['openid'])
                request.session['username'] = user.username
                request.session['userid'] = user.id
                if not user.verify:
                    request.session['origin'] = request.GET.get('state')
                    return redirect(reverse('center.user.authentication', args=[]))
            except ObjectDoesNotExist:
                pass
        else:
            req = urllib2.Request(
                'https://api.weixin.qq.com/sns/userinfo?access_token=' + response['access_token'] + '&openid=' +
                response['openid'] + '&lang=zh_CN')
            resp = urllib2.urlopen(req)
            content = resp.read()
            response = json.loads(content)
            request.session['userinfo'] = response
        return HttpResponseRedirect(request.GET.get('state'))


def oauth_getuserinfo(state='STATE', scope=1):
    if scope == 1:
        scope = 'snsapi_userinfo'  # 获取所有用户信息
    else:
        scope = 'snsapi_base'  # 获取openid,无需跳转
    return HttpResponseRedirect(
        'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + settings.APPID + '&redirect_uri=' + settings.DOMAIN + reverse(
            'wechat:oauth', args=[]) + '&response_type=code&scope=' + scope + '&state=' + state + '#wechat_redirect')


def oauth_test(request):
    if request.session.get('openid', default=False):
        print request.session.get('openid')
    else:
        return oauth_getuserinfo(state=request.get_full_path(), scope=2)


def getjsapi_ticket():
    jsapi_ticket = cache.get('jsapi_ticket')
    if not jsapi_ticket:
        get_jsapi_ticket = wechat.get_jsapi_ticket()
        jsapi_ticket = get_jsapi_ticket['jsapi_ticket']
        jsapi_ticket_expires_at = get_jsapi_ticket['jsapi_ticket_expires_at']
        cache.set('jsapi_ticket', jsapi_ticket, 7000)
        cache.set('jsapi_ticket_expires_at', jsapi_ticket_expires_at, 7000)
    else:
        jsapi_ticket_expires_at = cache.get('jsapi_ticket_expires_at')
    return {'jsapi_ticket': jsapi_ticket, 'jsapi_ticket_expires_at': jsapi_ticket_expires_at}
