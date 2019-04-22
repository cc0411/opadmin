# -*- coding:utf-8 -*-
from .wx_alert import WxApi
from django.core.mail.message import EmailMultiAlternatives


def deploy_mail(to_mail, cc_mail, *args):
    subject, body = gen_body(*args)
    msg = EmailMultiAlternatives(subject, body, to=[i.strip() for i in to_mail.split(',')],
                                 cc=[i.strip() for i in cc_mail.split(',')])
    msg.send()


def deploy_wx(*args):
    wx = WxApi('XXXXXXXXXXXXXX', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    subject, body = gen_body(*args)
    wx.send_msg(subject=subject, content=body)


def gen_body(*args):
    subject = '部署通知'
    body = """
    项目：{} 
    环境：{}
    操作：{}
    分支：{}
    版本：{}
    操作人：{}
    状态：{}
    """.format(*args)
    return subject, body