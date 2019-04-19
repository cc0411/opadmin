# -*- coding:utf-8 -*-
from django.conf.urls import url
from .views import DbAddView,DbDelView,DbUpdateView,DBConfList
urlpatterns = [
    url(r'^db/list/$', DBConfList.as_view(),name='db_list'),
    url(r'^db/add/$',DbAddView.as_view(),name='db_add'),
    url(r'^db/update/(?P<pk>\d+)/$',DbUpdateView.as_view(),name='db_update'),
    url(r'^db/delete/(?P<pk>\d+)/$',DbDelView.as_view(),name='db_delete'),
    ]