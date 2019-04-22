import os
import json
from django.http import JsonResponse, HttpResponse
from ansible_task.models import *
from .models import DeployLog,ProConfig,RepoConfig
from django.conf import settings
from .forms import RepoForm
from pure_pagination import PageNotAnInteger,EmptyPage,Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,View,UpdateView,CreateView,DeleteView,TemplateView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
import logging
logger = logging.getLogger(__name__)



class RepoListView(LoginRequiredMixin,ListView):
    model = RepoConfig
    template_name = 'pro/repo.html'
    context_object_name = 'all_repos'
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(RepoListView,self).get_context_data()
        context['title'] = '仓库列表'
        return  context
class RepoAddView(LoginRequiredMixin,CreateView):
    '''仓库添加'''
    model = RepoConfig
    form_class = RepoForm
    template_name =  'user/change.html'
    success_url = reverse_lazy('pro:repo_list')
    def get_context_data(self, **kwargs):
        context = super(RepoAddView,self).get_context_data()
        context['title'] = '新增仓库'
        return  context
class RepoUpdateView(LoginRequiredMixin,UpdateView):
    '''仓库修改'''
    model = RepoConfig
    form_class = RepoForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('pro:repo_list')
    def get_context_data(self, **kwargs):
        context = super(RepoUpdateView,self).get_context_data()
        context['title'] = '更新仓库'
        return  context
class RepoDelView(LoginRequiredMixin,DeleteView):

    '''仓库删除'''
    model = RepoConfig
    template_name = 'user/delete.html'
    success_url = reverse_lazy('pro:repo_list')
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(RepoDelView,self).get_context_data()
        context['cancel'] = reverse_lazy('pro:repo_list')
        context['title'] = '删除仓库'
        return  context


