# -*- coding:utf-8 -*-
from django.conf.urls import url
from .views import RepoDelView,RepoUpdateView,RepoAddView,RepoListView

urlpatterns = [
    url(r'^repo/list/$',RepoListView.as_view(),name='repo_list'),
    url(r'^repo/add/$',RepoAddView.as_view(),name='repo_add'),
    url(r'^repo/update/(?P<pk>\d+)/$',RepoUpdateView.as_view(),name='repo_update'),
    url(r'^repo/delete/(?P<pk>\d+)/$',RepoDelView.as_view(),name='repo_delete'),
]