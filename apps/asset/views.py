# -*- coding:utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,View,UpdateView,CreateView,DeleteView,TemplateView
from django.shortcuts import render,redirect,HttpResponse
from .models import HostGroup,Hosts,IDC,HostUsers,UserHostPer
from .forms import IdcForm,HostForm,HostUsersForm,HostGroupForm,UserHostPerForm
from pure_pagination import PageNotAnInteger,EmptyPage,Paginator
from django.db.models import Q
from django.core.urlresolvers import reverse_lazy
from django.http import FileResponse
import  xlrd
import os
from opadmin import settings
import  mimetypes
import logging
logger = logging.getLogger(__name__)

class HostListView(LoginRequiredMixin,ListView):
    template_name =  'host/hosts.html'
    model = Hosts
    context_object_name = 'all_hosts'
    queryset = Hosts.objects.all()
    ordering = ('-id')
    def get_queryset(self):
        self.queryset = super().get_queryset()
        search_keywords = self.request.GET.get('keywords','')
        if search_keywords:
            self.queryset = self.queryset.filter(Q(wip__icontains=search_keywords)|Q(hostname__icontains=search_keywords)|Q(nip__icontains=search_keywords))
        sort = self.request.GET.get('sort','')
        if sort:
            if sort =='ctime':
                self.queryset = self.queryset.order_by('-ctime')
            elif sort =='nip':
                self.queryset = self.queryset.order_by('-nip')
            elif sort =='wip':
                self.queryset = self.queryset.order_by('-wip')
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(self.queryset, 10, request=self.request)
        self.queryset = p.page(page)
        return self.queryset
    def get_context_data(self, **kwargs):
        context = super(HostListView,self).get_context_data()
        context['title'] = '主机列表'
        return  context

class IdcListView(LoginRequiredMixin,ListView):
    model = IDC
    template_name = 'host/idc.html'
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(IdcListView,self).get_context_data()
        context['title'] = '机房列表'
        return  context
class HostUserListView(LoginRequiredMixin,ListView):
    model = HostUsers
    template_name = 'host/hostuser.html'
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(HostUserListView,self).get_context_data()
        context['title'] = '远程用户列表'
        return  context

class UserHostPerListView(LoginRequiredMixin,ListView):
    template_name = 'host/user_host_per.html'
    model = UserHostPer
    context_object_name = 'all_user_hosts'
    queryset = UserHostPer.objects.all()
    ordering = ('-id')

    def get_queryset(self):
        self.queryset = super().get_queryset()
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(self.queryset, 1, request=self.request)
        self.queryset = p.page(page)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(UserHostPerListView, self).get_context_data()
        context['title'] = '用户主机授权'
        return context


class HostGroupListView(LoginRequiredMixin,ListView):
    model = HostGroup
    template_name = 'host/hostgroup.html'
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(HostGroupListView,self).get_context_data()
        context['title'] = '主机组列表'
        return  context

class HostAddView(LoginRequiredMixin,CreateView):
    '''主机添加'''
    model = Hosts
    form_class = HostForm
    template_name =  'user/change.html'
    success_url = reverse_lazy('host:host_list')
    def get_context_data(self, **kwargs):
        context = super(HostAddView,self).get_context_data()
        context['title'] = '新增主机'
        return  context

class HostUpdateView(LoginRequiredMixin,UpdateView):
    '''主机修改'''
    model = Hosts
    form_class = HostForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('host:host_list')
    def get_context_data(self, **kwargs):
        context = super(HostUpdateView,self).get_context_data()
        context['title'] = '更新主机'
        return  context

class HostDelView(LoginRequiredMixin,DeleteView):

    '''主机删除'''
    model = Hosts
    template_name = 'user/delete.html'
    success_url = reverse_lazy('host:host_list')
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(HostDelView,self).get_context_data()
        context['cancel'] = reverse_lazy('host:host_list')
        context['title'] = '删除主机'
        return  context

class  HostImportView(View):
    def get(self,request):
        return  render(request,'host/import.html')
    def post(self,request):
        context = {'status':True,'msg':'导入成功'}
        try:
            customer_excel = request.FILES.get('xlsfile')
            workbook = xlrd.open_workbook(file_contents=customer_excel.file.read())
            sheet = workbook.sheet_by_index(0)
            row_map = {
                0:{'text':'主机名','name':'hostname'},
                1:{'text':'外网地址','name':'wip'},
            }
            object_list = []
            for row_num in range(1,sheet.nrows):
                row = sheet.row(row_num)
                row_dict = {}
                for col_num,name_text in row_map.items():
                    row_dict[name_text['name']] = row[col_num].value
                object_list.append(Hosts(**row_dict))
            Hosts.objects.bulk_create(object_list,batch_size=20)
        except Exception as e:
            context['status'] = False
            context['msg'] = '导入错误'
        return render(request,'host/import.html',context)

class DownloadTplView(View):
    def get(self,request):
        tpl_path = os.path.join(settings.BASE_DIR,'asset','files','批量导入模板.xlsx')
        content_type = mimetypes.guess_type(tpl_path)[0]
        print(content_type)
        response = FileResponse(open(tpl_path,mode='rb'),content_type=content_type)
        response['Content-Disposition'] = "attachment;filename=%s" % 'host_excel_tpl.xlsx'
        return response

class HostUserAddView(LoginRequiredMixin,CreateView):
    '''远程用户添加'''
    model = HostUsers
    form_class = HostUsersForm
    template_name =  'user/change.html'
    success_url = reverse_lazy('host:hostuser_list')
    def get_context_data(self, **kwargs):
        context = super(HostUserAddView,self).get_context_data()
        context['title'] = '新增远程用户'
        return  context
class HostUserUpdateView(LoginRequiredMixin,UpdateView):
    '''远程用户修改'''
    model = HostUsers
    form_class = HostUsersForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('host:hostuser_list')
    def get_context_data(self, **kwargs):
        context = super(HostUserUpdateView,self).get_context_data()
        context['title'] = '更新远程用户'
        return  context
class HostUserDelView(LoginRequiredMixin,DeleteView):

    '''远程用户删除'''
    model = HostUsers
    template_name = 'user/delete.html'
    success_url = reverse_lazy('host:hostuser_list')
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(HostUserDelView,self).get_context_data()
        context['cancel'] = reverse_lazy('host:hostuser_list')
        context['title'] = '删除远程用户'
        return  context
class HostGroupAddView(LoginRequiredMixin,CreateView):
    '''主机组添加'''
    model = HostGroup
    form_class = HostGroupForm
    template_name =  'user/change.html'
    success_url = reverse_lazy('host:hostgroup_list')
    def get_context_data(self, **kwargs):
        context = super(HostGroupAddView,self).get_context_data()
        context['title'] = '新增主机组'
        return  context

class HostGroupUpdateView(LoginRequiredMixin,UpdateView):
    '''主机组修改'''
    model = HostGroup
    form_class = HostGroupForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('host:hostgroup_list')
    def get_context_data(self, **kwargs):
        context = super(HostGroupUpdateView,self).get_context_data()
        context['title'] = '更新主机组'
        return  context

class HostGroupDelView(LoginRequiredMixin,DeleteView):

    '''主机组删除'''
    model = HostGroup
    template_name = 'user/delete.html'
    success_url = reverse_lazy('host:hostgroup_list')
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(HostGroupDelView,self).get_context_data()
        context['cancel'] = reverse_lazy('host:hostgroup_list')
        context['title'] = '删除主机组'
        return  context

class IdcAddView(LoginRequiredMixin,CreateView):
    '''机房添加'''
    model = IDC
    form_class = IdcForm
    template_name =  'user/change.html'
    success_url = reverse_lazy('host:idc_list')
    def get_context_data(self, **kwargs):
        context = super(IdcAddView,self).get_context_data()
        context['title'] = '新增机房'
        return  context

class IdcUpdateView(LoginRequiredMixin,UpdateView):
    '''机房修改'''
    model = IDC
    form_class = IdcForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('host:idc_list')
    def get_context_data(self, **kwargs):
        context = super(IdcUpdateView,self).get_context_data()
        context['title'] = '更新机房'
        return  context

class IdcDelView(LoginRequiredMixin,DeleteView):

    '''机房删除'''
    model = IDC
    template_name = 'user/delete.html'
    success_url = reverse_lazy('host:idc_list')
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(IdcDelView,self).get_context_data()
        context['cancel'] = reverse_lazy('host:idc_list')
        context['title'] = '删除机房'
        return  context
class UserHostPerAddView(LoginRequiredMixin,CreateView):
    '''用户连接主机权限添加'''
    model = UserHostPer
    form_class = UserHostPerForm
    template_name =  'user/change.html'
    success_url = reverse_lazy('host:user_host_list')
    def get_context_data(self, **kwargs):
        context = super(UserHostPerAddView,self).get_context_data()
        context['title'] = '添加用户主机授权'
        return  context

class UserHostPerUpdateView(LoginRequiredMixin,UpdateView):
    '''用户连接主机权限修改'''
    model = UserHostPer
    form_class = UserHostPerForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('host:user_host_list')
    def get_context_data(self, **kwargs):
        context = super(UserHostPerUpdateView,self).get_context_data()
        context['title'] = '更新用户主机授权'
        return  context

class UserHostPerDelView(LoginRequiredMixin,DeleteView):

    '''用户连接主机权限删除'''
    model = UserHostPer
    template_name = 'user/delete.html'
    success_url = reverse_lazy('host:user_host_list')
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(UserHostPerDelView,self).get_context_data()
        context['cancel'] = reverse_lazy('host:user_host_list')
        context['title'] = '删除用户连接主机权限'
        return  context


class  WebSSH(LoginRequiredMixin,View):
    def  get(self,request):
        per = UserHostPer.objects.filter(user__username =request.user)
        for p  in per.all():
            hostgroup = p.host_groups.all()
            host = p.bind_hosts.all()
        return render(request,'host/webssh.html',locals())
