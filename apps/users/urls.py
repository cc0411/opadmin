# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import UserListView,RoleListView,MenuListView,UserProfileView
from .views import RoleAddView,MenuAddView,PermissionAddView,UserRegisterView
from .views import RoleUpdateView,MenuUpdateView,PermissionUpdateView,UserUpdatateView
from .views import RoleDelView,MenuDelView,PermissionDelView,UserDelView
from .views import SecondMenuAddView,SecondMenuDelView,SecondMenuUpdateView,multi_permissions,multi_permissions_del,distribute_permissions
urlpatterns = [
    url(r'^user/register/$', UserRegisterView.as_view(),name='register'),
    url(r'^user/list/$',UserListView.as_view(),name='user_list'),
    url(r'^user/profile/$',UserProfileView.as_view(),name='user_profile'),
    url(r'^menu/list/$',MenuListView.as_view(),name='menu_list'),
    url(r'^role/list/$',RoleListView.as_view(),name='role_list'),
    #url(r'^hostper/list/$',HostPermissionList.as_view(),name='hostper_list'),
    url(r'^role/add/$',RoleAddView.as_view(),name='role_add'),
    url(r'^menu/add/$',MenuAddView.as_view(),name='menu_add'),
    url(r'^permission/add/(?P<second_menu_id>\d+)/$',PermissionAddView.as_view(),name='permission_add'),
    #url(r'^hostper/add/$',HostPermissionCreate.as_view(),name='hostper_add'),
    url(r'^user/update/(?P<pk>[0-9]+)/$',UserUpdatateView.as_view(),name='user_update'),
    url(r'^role/update/(?P<pk>[0-9]+)/$',RoleUpdateView.as_view(),name='role_update'),
    url(r'^menu/update/(?P<pk>[0-9]+)/$',MenuUpdateView.as_view(),name='menu_update'),
    #url(r'^hostper/update/(?P<pk>[0-9]+)/$',HostPermissionUpdate.as_view(),name='hostper_update'),
    url(r'^permission/update/(?P<pk>[0-9]+)/$',PermissionUpdateView.as_view(),name='permission_update'),
    url(r'^user/delete/(?P<pk>[0-9]+)/$',UserDelView.as_view(),name='user_delete'),
    url(r'^role/delete/(?P<pk>[0-9]+)/$',RoleDelView.as_view(),name='role_delete'),
    url(r'^menu/delete/(?P<pk>[0-9]+)/$',MenuDelView.as_view(),name='menu_delete'),
    #url(r'^hostper/delete/(?P<pk>[0-9]+)/$',HostPermissionDel.as_view(),name='hostper_delete'),
    url(r'^permission/delete/(?P<pk>[0-9]+)/$',PermissionDelView.as_view(),name='permission_delete'),
    url(r'^multi/permissions/$', multi_permissions, name='multi_permissions'),
    url(r'^multi/permissions/delete/(?P<pk>\d+)/$', multi_permissions_del, name='multi_permissions_delete'),
    url(r'^distribute/permissions/$', distribute_permissions, name='distribute_permissions'),
    url(r'^second/menu/add/(?P<menu_id>\d+)$', SecondMenuAddView.as_view(), name='second_menu_add'),
    url(r'^second/menu/update/(?P<pk>\d+)/$', SecondMenuUpdateView.as_view(), name='second_menu_update'),
    url(r'^second/menu/delete/(?P<pk>\d+)/$', SecondMenuDelView.as_view(), name='second_menu_delete'),
    ]