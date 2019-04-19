from django.shortcuts import render
from django.views.generic import View,ListView,UpdateView,DeleteView,CreateView
from pure_pagination import PageNotAnInteger,EmptyPage,Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render,redirect,HttpResponse
from .models import DbLogs,DbConfig
from .utils import mysql_ops
from .forms import DbConfForm
# Create your views here.

class DBConfList(LoginRequiredMixin,ListView):
    '''数据库配置列表'''
    model = DbConfig
    template_name = 'db/dblist.html'
    context_object_name = 'all_db_list'
    queryset = DbConfig.objects.all()
    raise_exception = True
    ordering = ('-id')
    def get_queryset(self):
        self.queryset = super().get_queryset()
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(self.queryset, 10, request=self.request)
        self.queryset = p.page(page)
        return self.queryset
    def get_context_data(self, **kwargs):
        context = super(DBConfList, self).get_context_data()
        context['title'] = '数据库配置列表'
        return context

class DbAddView(LoginRequiredMixin,CreateView):
    '''数据库配置添加'''
    model = DbConfig
    form_class = DbConfForm
    template_name =  'user/change.html'
    success_url = reverse_lazy('db:db_list')
    def get_context_data(self, **kwargs):
        context = super(DbAddView,self).get_context_data()
        context['title'] = '新增数据库配置'
        return  context

class DbUpdateView(LoginRequiredMixin,UpdateView):
    '''数据库配置修改'''
    model = DbConfig
    form_class = DbConfForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('db:db_list')
    def get_context_data(self, **kwargs):
        context = super(DbUpdateView,self).get_context_data()
        context['title'] = '更新数据库配置'
        return  context

class DbDelView(LoginRequiredMixin,DeleteView):

    '''数据库配置删除'''
    model = DbConfig
    template_name = 'user/delete.html'
    success_url = reverse_lazy('db:db_list')
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(DbDelView,self).get_context_data()
        context['cancel'] = reverse_lazy('db:db_list')
        context['title'] = '删除数据库配置'
        return  context

class DbExecView(LoginRequiredMixin,View):
    raise_exception = True
    def get(self,request):
        db = DbConfig.objects.all()
        return render(request,'db/dbexec.html' )
    def post(self,request):
        pass

