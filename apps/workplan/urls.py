# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import OperationLogListView,CdnLogView,OperationLogAddView,OperationLogUpdateView,CdnLogAddView,CdnLogUpdateView

urlpatterns = [
    url(r'^operationlog/$', OperationLogListView.as_view(),name='operationloglist'),
    url(r'^cdnlog/$',CdnLogView.as_view(),name='cdnloglist'),
    url(r'^operationlogadd/$',OperationLogAddView.as_view(),name='operationlogadd'),
    url(r'^(?P<pk>[0-9]+)/operationlogupdate/$',OperationLogUpdateView.as_view(),name='operationlogupdate'),
    url(r'^cdnlogadd/$',CdnLogAddView.as_view(),name='cdnlogadd'),
    url(r'^(?P<pk>[0-9]+)/cdnlogupdate/$',CdnLogUpdateView.as_view(),name='cdnlogupdate'),
    ]