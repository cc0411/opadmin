# -*- coding:utf-8 -*-
from users.models import WxConfig
from django.core.cache import cache
import requests
def set_wx_token():
    corpid = WxConfig.objects.all()[0].corpid
    corpsecret = WxConfig.objects.all()[0].corp_secret
    token = requests.get(
        "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(corpid, corpsecret))
    if token.json()["errcode"] == 0:
        cache.set('wx_token', token.json()["access_token"], 7100)
