# -*- coding:utf-8 -*-
from django.conf.urls import url
from .views import HostListView,HostImportView,DownloadTplView,IdcListView,HostUserListView,HostGroupListView,UserHostPerListView
from .views import HostUpdateView,IdcUpdateView,HostUserUpdateView,HostGroupUpdateView,UserHostPerAddView
from .views import HostDelView,HostGroupDelView,IdcDelView,HostUserDelView,UserHostPerDelView
from  .views import HostAddView,IdcAddView,HostGroupAddView,HostUserAddView,UserHostPerUpdateView
from .views import WebSSH,AssetTableView
urlpatterns = [
    url(r'^host/list/$', HostListView.as_view(),name='host_list'),
    url(r'^hostper/list',UserHostPerListView.as_view(),name='user_host_list'),
    url(r'^import/$',HostImportView.as_view(),name='import'),
    url(r'^tpl/$',DownloadTplView.as_view(),name='tpl'),
    url(r'^idc/list/$',IdcListView.as_view(),name='idc_list'),
    url(r'^hostuser/list/$',HostUserListView.as_view(),name='hostuser_list'),
    url(r'^hostgroup/list/$',HostGroupListView.as_view(),name='hostgroup_list'),
    url(r'^host/add/$',HostAddView.as_view(),name='host_add'),
    url(r'^hostper/add/$',UserHostPerAddView.as_view(),name='hostper_add'),
    url(r'^hostper/update/(?P<pk>\d+)/$',UserHostPerUpdateView.as_view(),name='hostper_update'),
    url(r'^host/update/(?P<pk>\d+)/$',HostUpdateView.as_view(),name='host_update'),
    url(r'^host/delete/(?P<pk>\d+)/$',HostDelView.as_view(),name='host_delete'),
    url(r'^hostgroup/add/$',HostGroupAddView.as_view(),name='hostgroup_add'),
    url(r'^hostgroup/update/(?P<pk>\d+)/$',HostGroupUpdateView.as_view(),name='hostgroup_update'),
    url(r'^hostgroup/delete/(?P<pk>\d+)/$',HostGroupDelView.as_view(),name='hostgroup_delete'),
    url(r'^hostuser/add/$',HostUserAddView.as_view(),name='hostuser_add'),
    url(r'^hostuser/update/(?P<pk>\d+)/$',HostUserUpdateView.as_view(),name='hostuser_update'),
    url(r'^hostuser/delete/(?P<pk>\d+)/$',HostUserDelView.as_view(),name='hostuser_delete'),
    url(r'^idc/add/$',IdcAddView.as_view(),name='idc_add'),
    url(r'^idc/update/(?P<pk>\d+)/$',IdcUpdateView.as_view(),name='idc_update'),
    url(r'^idc/delete/(?P<pk>\d+)/$',IdcDelView.as_view(),name='idc_delete'),
    url(r'^hostper/delete/(?P<pk>\d+)/$',UserHostPerDelView.as_view(),name='hostper_delete'),
    url(r'^webssh/$',WebSSH.as_view(),name='webssh'),
    url(r'^assetjson/$',AssetTableView.as_view(),name='assetjson'),
    ]