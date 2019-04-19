# -*- coding:utf-8 -*-

from django.conf.urls import url
from .views import RunModule,GetInverntoryHost,PlayBookRun,PlaybooksAdd,AnsibleLogView
from .views import PlayBookList,PlayBookUpload,RoleDetail,RoleList,RoleUpdate,RoleAdd,RoleDel
from .views import PathCreate,PathDel,PlayBookDetail,GetFileContent,PlayBookDel
from .views import check_name,ModuleLogDel,PlayBookLogDel
from .views import InventoryDelView,InventoryUpdateView,InventoryListView,InventoryAddView
urlpatterns = [
    url(r'^inventory/list/$', InventoryListView.as_view(),name='inventory_list'),
    url(r'^inventory/add/$', InventoryAddView.as_view(), name='inventory_add'),
    url(r'^inventory/update/(?P<pk>\d+)/$', InventoryUpdateView.as_view(), name='inventory_update'),
    url(r'^inventory/delete/(?P<pk>\d+)/$', InventoryDelView.as_view(), name='inventory_delete'),
    url(r'^run_module/$', RunModule.as_view(), name='run_module'),
    url(r'^run_log/$', AnsibleLogView.as_view(), name='run_log'),
    url(r'^playbook/add/$', PlaybooksAdd.as_view(), name='playbook_add'),
    url(r'^playbook/upload/$', PlayBookUpload.as_view(), name='playbook_upload'),
    url(r'^playbook/list/$', PlayBookList.as_view(), name='playbook_list'),
    url(r'^role/detail/(?P<pk>[0-9]+)/$', RoleDetail.as_view(), name='role_detail'),
    url(r'^role/list/$', RoleList.as_view(), name='role_list'),
    url(r'^role/edit/$', RoleUpdate.as_view(), name='role_edit'),
    url(r'^role/add/$', RoleAdd.as_view(), name='role_add'),
    url(r'^path/del/$', PathDel.as_view(), name='path_del'),
    url(r'^path/create/$', PathCreate.as_view(), name='path_create'),
    url(r'^get_file_content/$', GetFileContent.as_view(), name='get_file_content'),
    url(r'^playbook/run/(?P<pk>[0-9]+)/$', PlayBookRun.as_view(), name='playbook_run'),
    url(r'^playbook/info/(?P<pk>[0-9]+)/$', PlayBookDetail.as_view(), name='playbook_info'),
    url(r'^playbook/del/(?P<pk>[0-9]+)/$', PlayBookDel.as_view(), name='playbook_del'),
    url(r'^role/del/(?P<pk>[0-9]+)/$', RoleDel.as_view(), name='role_del'),
    url(r'^playbook_log_del/$', PlayBookLogDel.as_view(), name='playbook_log_del'),
    url(r'^module_log_del/$', ModuleLogDel.as_view(), name='module_log_del'),
    url(r'^check_name/$', check_name, name='check_name'),
    url(r'^get_inventory_hosts/$',GetInverntoryHost.as_view() , name='get_inventory_hosts')
]