# -*- coding:utf-8 -*-
from django.conf.urls import url
from .views import SshLogPlay,SshTerminalKill,SshTerminalMonitor,BatchCommandExecute,SshConnect,DynamicPassword,AuditLogList,CommandLogList,FilemanageView
urlpatterns = [
    url(r'^sshconnect/(?P<ip>(?:(?:0|1[\d]{0,2}|2(?:[0-4]\d?|5[0-5]?|[6-9])?|[3-9]\d?)\.){3}(?:0|1[\d]{0,2}|2(?:[0-4]\d?|5[0-5]?|[6-9])?|[3-9]\d?))/(?P<serverid>[0-9]+)/$',
        SshConnect.as_view(), name='sshconnect'),
    url(r'^filemanage/(?P<ip>(?:(?:0|1[\d]{0,2}|2(?:[0-4]\d?|5[0-5]?|[6-9])?|[3-9]\d?)\.){3}(?:0|1[\d]{0,2}|2(?:[0-4]\d?|5[0-5]?|[6-9])?|[3-9]\d?))/(?P<serverid>[0-9]+)/$',FilemanageView.as_view(), name='filemanage'),
    url(r'^batchcommandexecute/$', BatchCommandExecute.as_view(),
        name='batchcommandexecute'),
    url(r'^sshterminalkill/$', SshTerminalKill.as_view(), name='sshterminalkill'),
    url(r'^sshlogplay/(?P<pk>[0-9]+)/$',
        SshLogPlay.as_view(), name='sshlogplay'),
    url(r'^sshterminalmonitor/(?P<pk>[0-9]+)/',
        SshTerminalMonitor.as_view(), name='sshterminalmonitor'),
    url(r'^dynamicpassword/$', DynamicPassword.as_view(), name='dynamicpassword'),
    url(r'^auditlog/list/$',AuditLogList.as_view(),name='auditlog_list'),
    url(r'^commandlog/list/$',CommandLogList.as_view(),name='commandlog_list'),


]