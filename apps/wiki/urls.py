# -*- coding:utf-8 -*-
from django.conf.urls import url
from .views import DocAddView,DocUpdateView,DocDetailView,DocListView,DocDelView
urlpatterns = [
    url(r'^doc/list/$',DocListView.as_view(),name='doc_list'),
    url(r'^doc/detail/(?P<pk>[0-9]+)/$',DocDetailView.as_view(),name='doc_detail'),
    url(r'^doc/add/$',DocAddView.as_view(),name='doc_add'),
    url(r'^doc/update/(?P<pk>[0-9]+)/$',DocUpdateView.as_view(),name='doc_update'),
    url(r'^doc/delete/(?P<pk>[0-9]+)/$',DocDelView.as_view(),name='doc_delete'),
]