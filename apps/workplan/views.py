# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,View,UpdateView,CreateView
from django.shortcuts import render,redirect
from .models import CdnLog,OperationLog
from .forms import OperationLogForm,CdnLogForm
from pure_pagination import PageNotAnInteger,EmptyPage,Paginator
from django.db.models import Q
import time,datetime
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404

def format_time(t):
    s = time.strptime(t, "%m/%d/%Y")
    day = int(time.strftime("%d",s))
    month = int(time.strftime("%m",s))
    year = int(time.strftime("%Y",s))
    tm = datetime.date(year,month,day)
    return  tm


class OperationLogListView(LoginRequiredMixin,View):
    def get(self,request):
        all_logs = OperationLog.objects.filter(user=request.user.name)
        try:
            page = request.GET.get('page',1)
        except PageNotAnInteger:
            page =1
        p = Paginator(all_logs,10,request=request)
        logs = p.page(page)

        return  render(request,'work/operationloglist.html',{
            "all_logs":logs
        })


class  OperationLogAddView(LoginRequiredMixin,CreateView):
    model = OperationLog
    form_class = OperationLogForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('workplan:operationloglist')
    def get_initial(self):
        initial = super(OperationLogAddView, self).get_initial()
        initial['user'] = self.request.user.name
        return initial
    def get_context_data(self, **kwargs):
        context = super(OperationLogAddView, self).get_context_data()
        context['title'] = '新增运维操作日志'
        return context
    def get_form(self, form_class=None):
        form = super(OperationLogAddView, self).get_form(form_class)
        form.fields['user'].widget.attrs.update({'readonly': True})
        return form

class OperationLogUpdateView(LoginRequiredMixin,UpdateView):
    model = OperationLog
    form_class = OperationLogForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('workplan:operationloglist')
    def get_context_data(self, **kwargs):
        context = super(OperationLogUpdateView,self).get_context_data()
        context['title'] = '更新运维操作日志'
        return  context
    def get_form(self, form_class=None):
        form = super(OperationLogUpdateView, self).get_form(form_class)
        form.fields['user'].widget.attrs.update({'readonly': True})
        return form

class CdnLogView(LoginRequiredMixin,View):
    def get(self,request):

        all_logs = CdnLog.objects.filter(user=request.user.name)
        starttime = request.GET.get('starttime','01/01/2019')
        endtime = request.GET.get('endtime','01/01/2019')
        format_starttime = format_time(starttime)
        formt_endtime = format_time(endtime)
        print(format_starttime,formt_endtime)
        s = all_logs.filter(ctime__range=(format_starttime,formt_endtime))

        print(s)
        try:
            page = request.GET.get('page',1)
        except PageNotAnInteger:
            page =1
        p = Paginator(all_logs,10,request=request)
        logs = p.page(page)

        return  render(request,'work/cdnloglist.html',{
            "all_logs":logs
        })
class  CdnLogAddView(LoginRequiredMixin,CreateView):
    model = CdnLog
    form_class = CdnLogForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('workplan:cdnloglist')
    def get_initial(self):
        initial = super(CdnLogAddView, self).get_initial()
        initial['user'] = self.request.user.name
        return initial
    def get_context_data(self, **kwargs):
        context = super(CdnLogAddView, self).get_context_data()
        context['title'] = '新增CDN操作日志'
        return context
    def get_form(self, form_class=None):
        form = super(CdnLogAddView, self).get_form(form_class)
        form.fields['user'].widget.attrs.update({'readonly': True})
        return form

class CdnLogUpdateView(LoginRequiredMixin,UpdateView):
    model = CdnLog
    form_class = CdnLogForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('workplan:cdnloglist')
    def get_context_data(self, **kwargs):
        context = super(CdnLogUpdateView,self).get_context_data()
        context['title'] = '更新运维操作日志'
        return  context
    def get_form(self, form_class=None):
        form = super(CdnLogUpdateView, self).get_form(form_class)
        form.fields['user'].widget.attrs.update({'readonly': True})
        return form
