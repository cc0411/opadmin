# -*- coding: utf-8 -*-
from django.views.generic import View,UpdateView,CreateView,FormView,DeleteView,ListView
from django.shortcuts import render,redirect,HttpResponse
from django.core.cache import cache
from utils.common import set_wx_token
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.conf import settings
from django.utils.module_loading import import_string
from collections import OrderedDict
from django.forms import formset_factory
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate,login,logout
from users.forms.users import LoginForm,RegisterForm,UploadImageForm
from users.forms.menu import RoleForm,MenuForm,PermissionForm,SecondMenuModelForm,MultiAddPermissionForm,MultiEditPermissionForm
from .service.init_permissions import initial_session
from .models import Role,Permission,Menu,WxConfig
from django.core.urlresolvers import reverse_lazy
from users.service.urls import  memory_reverse
from users.service.routes import get_all_url_dict
from pure_pagination import PageNotAnInteger,EmptyPage,Paginator
from asset.models import Hosts
User = get_user_model()
import json
import requests
import logging
logger = logging.getLogger(__name__)
class CustomBackend(ModelBackend):
    '''自定义登录方式'''
    def authenticate(self, request,username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None

class LoginView(View):
    '''登录页面'''
    def get(self,request):
        wx = {
            "appid": WxConfig.objects.all()[0].corpid ,
            "agentid": WxConfig.objects.all()[0].agentid ,
            "redirect_uri": WxConfig.objects.all()[0].redirect_uri ,
            "state": WxConfig.objects.all()[0].state ,
        }
        return render(request,'login.html',wx)
    def post(self,request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():

            username = request.POST.get('username','')
            password = request.POST.get('password','')
            user = authenticate(username=username,password=password)

            if user is not None:
                login(request,user)
                initial_session(user,request)
                return redirect('/index/')
            else:
                return render(request,"login.html",{"msg":"用户名或者密码错误"})
        else:
            return render(request,'login.html',{'login_form':login_form})

class WxLogin(View):
    def get(self,request):
        code = request.GET.get("code")
        if not cache.get("wx_token"):
            set_wx_token()
        wx_token = cache.get("wx_token")
        playload = {
            'access_token':wx_token,
            'code':code,
        }
        r = requests.get("https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo", params=playload)
        if r.json()["errcode"] != 0:
            return redirect('/login/')
        userid = r.json()['UserId']
        u = requests.get('https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={0}&userid={1}'.format(wx_token,userid))
        data = u.json()
        try:
            user,created = User.objects.update_or_create(username=userid,defaults={'name':data['name'],'mobile':data['mobile'],'email':data['email']})
            #下面代码采用django signals实现
            #if created:
            #    #授权基本的权限，因为我普通用户的角色id是4
            #    user.roles.add(4)
        except Exception as e:
            print(e)
        finally:
            login(request, user)
            initial_session(user, request)
        return redirect('/index/')


class LogoutView(View):
    '''注销页面'''
    def get(self, request):
        # django自带的logout
        logout(request)
        # 重定向到首页,
        return redirect(reverse("login"))

class Dashboard(LoginRequiredMixin,View):
    '''首页'''
    login_url = '/login/'
    redirect_field_name = 'next'
    def get(self,request):
        asset_count = Hosts.objects.count()
        instance_count = Hosts.objects.filter(server_type='instance').count()
        physical_count = Hosts.objects.filter(server_type ='physical').count()
        virtual_count = Hosts.objects.filter(server_type='virtual').count()
        online_count = Hosts.objects.filter(status='online').count()
        offline_count = Hosts.objects.filter(status='offline').count()
        user_count = User.objects.count()
        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        permission_list =[]
        for k, v in  permission_dict.items():
            permission_list.append(v['title'])

        return  render(request,'index.html',locals())

class UserRegisterView(LoginRequiredMixin,FormView):
    '''新增用户'''
    template_name = 'user/change.html'
    form_class = RegisterForm
    success_url = reverse_lazy('user:user_list')
    raise_exception = True
    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']
        name = form.cleaned_data['name']
        mobile = form.cleaned_data['mobile']
        roles = form.cleaned_data['roles']
        data =User.objects.create_user(username=username,
                                 password=password,
                                 email=email,
                                 name=name,
                                 mobile=mobile,
                                 is_staff=True,
                                 is_active = True)
        data.roles.add(*roles)
        data.save()
        return redirect(self.get_success_url())
    def get_context_data(self, **kwargs):
        context = super(UserRegisterView,self).get_context_data()
        context['title'] = '新增用户'
        return  context

class UserListView(LoginRequiredMixin,ListView):
    '''用户列表'''
    template_name =  'user/userlist.html'
    model = User
    context_object_name = 'all_users'
    queryset = User.objects.all()
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
        context = super(UserListView,self).get_context_data()
        context['title'] = '用户列表'
        return  context
class UserProfileView(LoginRequiredMixin,View):
    '''用户详情页'''
    def get(self,request):
        user = User.objects.get(username=request.user)
        return render(request,'user/userprofile.html',locals())

    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse(
                '{"status":"success"}',
                content_type='application/json')
        else:
            return HttpResponse(
                '{"status":"fail"}',
                content_type='application/json')


class UserDelView(LoginRequiredMixin,DeleteView):
    '''删除用户'''
    model = User
    template_name = 'user/delete.html'
    success_url = reverse_lazy('user:user_list')
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(UserDelView, self).get_context_data()
        context['cancel'] = reverse_lazy('user:user_list')
        context['title'] = '删除用户'
        return context
class UserUpdatateView(LoginRequiredMixin,UpdateView):
    '''用户信息更新'''
    template_name = 'user/change.html'
    model = User
    form_class = RegisterForm
    success_url = reverse_lazy('user:user_list')
    raise_exception = True

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        data = self.get_object()
        initial = super(UserUpdatateView, self).get_initial()
        initial['username'] = data.username
        initial['email'] = data.email
        initial['mobile'] = data.mobile
        initial['name'] = data.name
        initial['roles'] = data.roles.all()
        return initial

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        mobile = form.cleaned_data['mobile']
        roles = form.cleaned_data['roles']
        data = self.get_object()

        if len(password) != 0:
            data.set_password(password)
        data.email = email
        data.name = name
        data.mobile = mobile
        data.roles = roles
        data.save()
        return redirect(self.get_success_url())

    def get_form(self, form_class=None):
        form = super(UserUpdatateView, self).get_form(form_class)
        form.fields['username'].widget.attrs.update({'readonly': True})
        form.fields['password'].required = False
        form.fields['password2'].required = False
        return form
    def get_context_data(self, **kwargs):
        context = super(UserUpdatateView,self).get_context_data()
        context['title'] = '编辑用户'
        return  context

class RoleListView(LoginRequiredMixin,ListView):

    '''角色列表'''
    template_name = 'user/rolelist.html'
    model = Role
    context_object_name = 'all_roles'
    queryset = Role.objects.all()
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
        context = super(RoleListView,self).get_context_data()
        context['title'] = '角色列表'
        return  context

class RoleAddView(LoginRequiredMixin,CreateView):
    '''角色添加'''
    model = Role
    form_class = RoleForm
    template_name =  'user/change.html'
    success_url = reverse_lazy('user:role_list')
    def get_context_data(self, **kwargs):
        context = super(RoleAddView,self).get_context_data()
        context['title'] = '新增角色'
        return  context

class RoleUpdateView(LoginRequiredMixin,UpdateView):
    '''角色修改'''
    model = Role
    form_class = RoleForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('user:role_list')
    def get_context_data(self, **kwargs):
        context = super(RoleUpdateView,self).get_context_data()
        context['title'] = '更新角色'
        return  context

class RoleDelView(LoginRequiredMixin,DeleteView):

    '''角色删除'''
    model = Role
    template_name = 'user/delete.html'
    success_url = reverse_lazy('user:role_list')
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(RoleDelView,self).get_context_data()
        context['cancel'] = reverse_lazy('user:role_list')
        context['title'] = '删除角色'
        return  context

class  MenuListView(LoginRequiredMixin,View):
    '''菜单列表'''
    def get(self,request):
        menus = Menu.objects.all()
        menu_id = request.GET.get('mid')  #选择一级菜单
        second_menu_id = request.GET.get('sid')  #选择二级菜单
        menu_exists = Menu.objects.filter(id=menu_id).exists()
        if not menu_exists:
            menu_id = None
        if menu_id:
            second_menus = Permission.objects.filter(menu_id=menu_id)
        else:
            second_menus = []
        second_menu_exists = Permission.objects.filter(id=second_menu_id).exists()
        if not  second_menu_exists:
            second_menu_id = None
        if second_menu_id:
            permisssions = Permission.objects.filter(pid_id=second_menu_id)
        else:
            permisssions = []
        return render(request,'user/menulist.html',{'menus':menus,'second_menus':second_menus,'menu_id':menu_id,'permissions':permisssions,'second_menu_id':second_menu_id})

class MenuAddView(LoginRequiredMixin,CreateView):
    '''菜单添加'''
    model = Menu
    form_class = MenuForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('user:menu_list')
    def get_context_data(self, **kwargs):
        context = super(MenuAddView,self).get_context_data()
        context['title'] = '新建菜单'
        return  context

class MenuUpdateView(LoginRequiredMixin,UpdateView):
    '''菜单更新'''
    model = Menu
    form_class = MenuForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('user:menu_list')
    def get_context_data(self, **kwargs):
        context = super(MenuUpdateView,self).get_context_data()
        context['title'] = '更新菜单'
        return  context

class MenuDelView(LoginRequiredMixin,DeleteView):
    '''菜单删除'''
    model = Menu
    template_name = 'user/delete.html'
    success_url = reverse_lazy('user:menu_list')
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(MenuDelView, self).get_context_data()
        context['cancel'] = reverse_lazy('user:menu_list')
        context['title'] = '删除角色'
        return context

class SecondMenuAddView(LoginRequiredMixin,View):
    '''二级菜单添加'''
    def get(self,request,menu_id):
        title = '添加二级菜单'
        menu_obj = Menu.objects.filter(id=menu_id).first()
        form = SecondMenuModelForm(initial={'menu':menu_obj})
        return render(request,'user/change.html',{'form':form,'title':title})
    def post(self,request,menu_id):
        form = SecondMenuModelForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(memory_reverse(request,'user:menu_list'))
        return  render(request,'user/change.html',{'form':form})

class SecondMenuUpdateView(LoginRequiredMixin,View):
    '''二级菜单更新'''
    def get(self,request,pk):
        title ='修改二级菜单'
        permission_obj = Permission.objects.filter(id=pk).first()
        form = SecondMenuModelForm(instance=permission_obj)
        return render(request,'user/change.html',{'form':form,'title':title})
    def post(self,request,pk):
        permission_obj = Permission.objects.filter(id=pk).first()
        form = SecondMenuModelForm(data=request.POST,instance=permission_obj)
        if form.is_valid():
            form.save()
            return redirect(memory_reverse(request,'user:menu_list'))
        return render(request,'user/change.html',{'form':form})

class SecondMenuDelView(LoginRequiredMixin,DeleteView):
    '''二级菜单删除'''
    model = Permission
    template_name = 'user/delete.html'
    success_url = reverse_lazy('user:menu_list')
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(SecondMenuDelView, self).get_context_data()
        context['cancel'] = reverse_lazy('user:menu_list')
        context['title'] = '删除权限'
        return context
class PermissionAddView(LoginRequiredMixin,View):
    '''权限添加'''
    def get(self,request,second_menu_id):
        title = '添加权限'
        form = PermissionForm()
        return  render(request,'user/change.html',{'form':form,'title':title})
    def post(self,request,second_menu_id):
        form = PermissionForm(data=request.POST)
        if form.is_valid():
            second_menu_obj = Permission.objects.filter(id=second_menu_id).first()
            if not second_menu_obj:
                return HttpResponse('二级菜单不存在')
            form.instance.pid = second_menu_obj
            form.save()
            return redirect(memory_reverse(request,'user:menu_list'))


class PermissionUpdateView(LoginRequiredMixin,UpdateView):
    '''权限更新'''
    model = Permission
    form_class = PermissionForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('user:menu_list')

    def get_context_data(self, **kwargs):
        context = super(PermissionUpdateView, self).get_context_data()
        context['title'] = '更新权限'
        return context
class PermissionDelView(LoginRequiredMixin,DeleteView):
    '''权限删除'''
    model = Permission
    template_name = 'user/delete.html'
    success_url = reverse_lazy('user:menu_list')
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(PermissionDelView, self).get_context_data()
        context['cancel'] = reverse_lazy('user:menu_list')
        context['title'] = '删除权限'
        return context
def multi_permissions(request):
    """
    批量操作权限
    :param request:
    :return:
    """
    post_type = request.GET.get('type')
    generate_formset_class = formset_factory(MultiAddPermissionForm, extra=0)
    update_formset_class = formset_factory(MultiEditPermissionForm, extra=0)

    generate_formset = None
    update_formset = None
    if request.method == 'POST' and post_type == 'generate':
        # pass # 批量添加
        formset = generate_formset_class(data=request.POST)
        if formset.is_valid():
            object_list = []
            post_row_list = formset.cleaned_data
            has_error = False
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                try:
                    new_object = Permission(**row_dict)
                    new_object.validate_unique()
                    object_list.append(new_object)
                except Exception as e:
                    formset.errors[i].update(e)
                    generate_formset = formset
                    has_error = True
            if not has_error:
                Permission.objects.bulk_create(object_list, batch_size=100)
        else:
            generate_formset = formset

    if request.method == 'POST' and post_type == 'update':
        # pass  # 批量更新
        formset = update_formset_class(data=request.POST)
        if formset.is_valid():
            post_row_list = formset.cleaned_data
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                permission_id = row_dict.pop('id')
                try:
                    row_object = Permission.objects.filter(id=permission_id).first()
                    for k, v in row_dict.items():
                        setattr(row_object, k, v)
                    row_object.validate_unique()
                    row_object.save()
                except Exception as e:
                    formset.errors[i].update(e)
                    update_formset = formset
        else:
            update_formset = formset

    # 1. 获取项目中所有的URL
    all_url_dict = get_all_url_dict()
    """
    {
        'rbac:role_list':{'name': 'rbac:role_list', 'url': '/rbac/role/list/'},
        'rbac:role_add':{'name': 'rbac:role_add', 'url': '/rbac/role/add/'},
        ....
    }
    """
    router_name_set = set(all_url_dict.keys())

    # 2. 获取数据库中所有的URL
    permissions = Permission.objects.all().values('id', 'title', 'name', 'url', 'menu_id', 'pid_id')
    permission_dict = OrderedDict()
    permission_name_set = set()
    for row in permissions:
        permission_dict[row['name']] = row
        permission_name_set.add(row['name'])
    """
    {
        'rbac:role_list': {'id':1,'title':'角色列表',name:'rbac:role_list',url.....},
        'rbac:role_add': {'id':1,'title':'添加角色',name:'rbac:role_add',url.....},
        ...
    }
    """

    for name, value in permission_dict.items():
        router_row_dict = all_url_dict.get(name)  # {'name': 'rbac:role_list', 'url': '/rbac/role/list/'},
        if not router_row_dict:
            continue
        if value['url'] != router_row_dict['url']:
            value['url'] = '路由和数据库中不一致'

    # 3. 应该添加、删除、修改的权限有哪些？
    # 3.1 计算出应该增加的name
    if not generate_formset:
        generate_name_list = router_name_set - permission_name_set
        generate_formset = generate_formset_class(
            initial=[row_dict for name, row_dict in all_url_dict.items() if name in generate_name_list])

    # 3.2 计算出应该删除的name
    delete_name_list = permission_name_set - router_name_set
    delete_row_list = [row_dict for name, row_dict in permission_dict.items() if name in delete_name_list]

    # 3.3 计算出应该更新的name
    if not update_formset:
        update_name_list = permission_name_set & router_name_set
        update_formset = update_formset_class(
            initial=[row_dict for name, row_dict in permission_dict.items() if name in update_name_list])
    return render(
        request,
        'user/multi_permissions.html',
        {
            'generate_formset': generate_formset,
            'delete_row_list': delete_row_list,
            'update_formset': update_formset,
        }
    )
def multi_permissions_del(request, pk):
    """
    批量页面的权限删除
    :param request:
    :param pk:
    :return:
    """
    url = memory_reverse(request, 'user:multi_permissions')
    if request.method == 'GET':
        return render(request, 'user/delete.html', {'cancel': url})

    Permission.objects.filter(id=pk).delete()
    return redirect(url)
def distribute_permissions(request):
    """
    权限分配
    :param request:
    :return:
    """

    user_id = request.GET.get('uid')
    # 业务中的用户表 "users.models.UserProfile""
    user_model_class = import_string(settings.RBAC_USER_MODLE_CLASS)

    user_object = user_model_class.objects.filter(id=user_id).first()
    if not user_object:
        user_id = None

    role_id = request.GET.get('rid')
    role_object = Role.objects.filter(id=role_id).first()
    if not role_object:
        role_id = None

    if request.method == 'POST' and request.POST.get('type') == 'role':
        role_id_list = request.POST.getlist('roles')
        # 用户和角色关系添加到第三张表（关系表）
        if not user_object:
            return HttpResponse('请选择用户，然后再分配角色！')
        user_object.roles.set(role_id_list)

    if request.method == 'POST' and request.POST.get('type') == 'permission':
        permission_id_list = request.POST.getlist('permissions')
        if not role_object:
            return HttpResponse('请选择角色，然后再分配权限！')
        role_object.permissions.set(permission_id_list)

    # 获取当前用户拥有的所有角色
    if user_id:
        user_has_roles = user_object.roles.all()
    else:
        user_has_roles = []

    user_has_roles_dict = {item.id: None for item in user_has_roles}

    # 获取当前用户用户用户的所有权限

    # 如果选中的角色，优先显示选中角色所拥有的权限
    # 如果没有选择角色，才显示用户所拥有的权限
    if role_object:  # 选择了角色
        user_has_permissions = role_object.permissions.all()
        user_has_permissions_dict = {item.id: None for item in user_has_permissions}

    elif user_object:  # 未选择角色，但选择了用户
        user_has_permissions = user_object.roles.filter(permissions__id__isnull=False).values('id',
                                                                                              'permissions').distinct()
        user_has_permissions_dict = {item['permissions']: None for item in user_has_permissions}
    else:
        user_has_permissions_dict = {}

    all_user_list = user_model_class.objects.all()

    all_role_list = Role.objects.all()

    menu_permission_list = []

    # 所有的菜单（一级菜单）
    all_menu_list = Menu.objects.values('id', 'title')
    """
    [
        {id:1,title:菜单1,children:[{id:1,title:x1, menu_id:1,'children':[{id:11,title:x2,pid:1},] },{id:2,title:x1, menu_id:1 },]},
        {id:2,title:菜单2,children:[{id:3,title:x1, menu_id:2 },{id:5,title:x1, menu_id:2 },]},
        {id:3,title:菜单3,children:[{id:4,title:x1, menu_id:3 },]},
    ]
    """
    all_menu_dict = {}
    """
       {
           1:{id:1,title:菜单1,children:[{id:1,title:x1, menu_id:1,children:[{id:11,title:x2,pid:1},] },{id:2,title:x1, menu_id:1,children:[] },]},
           2:{id:2,title:菜单2,children:[{id:3,title:x1, menu_id:2,children:[] },{id:5,title:x1, menu_id:2,children:[] },]},
           3:{id:3,title:菜单3,children:[{id:4,title:x1, menu_id:3,children:[] },]},
       }
       """
    for item in all_menu_list:
        item['children'] = []
        all_menu_dict[item['id']] = item

    # 所有二级菜单
    all_second_menu_list = Permission.objects.filter(menu__isnull=False).values('id', 'title', 'menu_id')

    """
    [
        {id:1,title:x1, menu_id:1,children:[{id:11,title:x2,pid:1},] },   
        {id:2,title:x1, menu_id:1,children:[] },
        {id:3,title:x1, menu_id:2,children:[] },
        {id:4,title:x1, menu_id:3,children:[] },
        {id:5,title:x1, menu_id:2,children:[] },
    ]
    """
    all_second_menu_dict = {}
    """
        {
            1:{id:1,title:x1, menu_id:1,children:[{id:11,title:x2,pid:1},] },   
            2:{id:2,title:x1, menu_id:1,children:[] },
            3:{id:3,title:x1, menu_id:2,children:[] },
            4:{id:4,title:x1, menu_id:3,children:[] },
            5:{id:5,title:x1, menu_id:2,children:[] },
        }
        """
    for row in all_second_menu_list:
        row['children'] = []
        all_second_menu_dict[row['id']] = row

        menu_id = row['menu_id']
        all_menu_dict[menu_id]['children'].append(row)

    # 所有三级菜单（不能做菜单的权限）
    all_permission_list = Permission.objects.filter(menu__isnull=True).values('id', 'title', 'pid_id')
    """
    [
        {id:11,title:x2,pid:1},
        {id:12,title:x2,pid:1},
        {id:13,title:x2,pid:2},
        {id:14,title:x2,pid:3},
        {id:15,title:x2,pid:4},
        {id:16,title:x2,pid:5},
    ]
    """
    for row in all_permission_list:
        pid = row['pid_id']
        if not pid:
            continue
        all_second_menu_dict[pid]['children'].append(row)

    """
    [
        {
            id:1,
            title:'业务管理'
            children:[
                {
                    'id':11, 
                    title:'账单列表',
                    children:[
                        {'id':12,title:'添加账单'}
                    ]
                },
                {'id':11, title:'客户列表'},
            ]
        },

    ]
    """

    return render(
        request,
        'user/distribute_permissions.html',
        {
            'user_list': all_user_list,
            'role_list': all_role_list,
            'all_menu_list': all_menu_list,
            'user_id': user_id,
            'role_id': role_id,
            'user_has_roles_dict': user_has_roles_dict,
            'user_has_permissions_dict': user_has_permissions_dict,
        }
    )

#class HostPermissionCreate(LoginRequiredMixin, CreateView):
#    model = HostPermission
#    form_class = HostPermissionForm
#    success_url = reverse_lazy('user:hostper_list')
#    template_name = 'user/change.html'
#    raise_exception = True
#
#    def get_context_data(self, **kwargs):
#        context = super(HostPermissionCreate, self).get_context_data(**kwargs)
#        context['title'] = "创建主机管理权限"
#        return context
#
#    def form_valid(self, form):
#        user = form.cleaned_data['user']
#        permissionset = form.cleaned_data['permissions']
#        user.user_permissions.clear()
#        user.user_permissions.add(*permissionset)
#        user.save()
#        self.object = form.save()
#        return super(HostPermissionCreate, self).form_valid(form)
#
#    def get_form(self, form_class=None):
#        form = super(HostPermissionCreate, self).get_form(form_class)
#        form.fields['permissions'].widget.attrs.update(
#            {'checked': 'checked'})
#        return form
#
#class HostPermissionList(LoginRequiredMixin,View):
#    def get(self,request):
#        all_permissions = HostPermission.objects.all()
#        try:
#            page = request.GET.get('page', 1)
#        except PageNotAnInteger:
#            page = 1
#        p = Paginator(all_permissions, 10, request=request)
#        permissions = p.page(page)
#
#        return render(request, 'user/hostpermissionlist.html', {
#            "all_permissions": permissions
#        })
#class HostPermissionUpdate(LoginRequiredMixin,UpdateView):
#    model = HostPermission
#    form_class = HostPermissionForm
#    success_url = reverse_lazy('user:host_perlist')
#    template_name = 'user/change.html'
#    raise_exception = True
#
#    def get_context_data(self, **kwargs):
#        context = super(HostPermissionUpdate, self).get_context_data(**kwargs)
#        context['title'] = "更新主机管理权限"
#        return context
#
#    def form_valid(self, form):
#        user = form.cleaned_data['user']
#        permissionset = form.cleaned_data['permissions']
#        user.user_permissions.clear()
#        user.user_permissions.add(*permissionset)
#        user.save()
#        self.object = form.save()
#        return super(HostPermissionUpdate, self).form_valid(form)
#
#class HostPermissionDel(LoginRequiredMixin,DeleteView):
#    model = HostPermission
#    template_name = 'user/delete.html'
#    success_url = reverse_lazy('user:hostper_list')
#    raise_exception = True
#
#    def get_context_data(self, **kwargs):
#        context = super(HostPermissionDel, self).get_context_data()
#        context['cancel'] = reverse_lazy('user:hostper_list')
#        context['title'] = '删除主机权限'
#        return context
