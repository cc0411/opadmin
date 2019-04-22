import os
import json
import zipfile
import shutil
from ansible_task.utils.gen_resource import GenResource
from django.http import JsonResponse, HttpResponse
from ansible_task.models import *
from asset.models import Hosts
from django.conf import settings
from pure_pagination import PageNotAnInteger,EmptyPage,Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,View,UpdateView,CreateView,DeleteView,TemplateView
from django.core.urlresolvers import reverse_lazy
from .forms import InventoryForm
from django.shortcuts import render
from webterminal.utils import mkdir_p
import logging
logger = logging.getLogger(__name__)


class InventoryListView(LoginRequiredMixin,View):
    '''动态主机列表Inventory'''
    def get(self,request):
        all_inventorys = Inventory.objects.all()
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_inventorys, 1, request=request)
        inventorys = p.page(page)

        return render(request, 'task/inventory.html', {
            "all_inventorys": inventorys
        })

class InventoryAddView(LoginRequiredMixin,CreateView):
    '''动态主机组添加'''
    model = Inventory
    form_class = InventoryForm
    template_name =  'user/change.html'
    success_url = reverse_lazy('ansible_task:inventory_list')
    def get_context_data(self, **kwargs):
        context = super(InventoryAddView,self).get_context_data()
        context['title'] = '新增动态主机组'
        return  context

class InventoryUpdateView(LoginRequiredMixin,UpdateView):
    '''动态主机组修改'''
    model = Inventory
    form_class = InventoryForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('ansible_task:inventory_list')
    def get_context_data(self, **kwargs):
        context = super(InventoryUpdateView,self).get_context_data()
        context['title'] = '更新动态主机组'
        return  context

class InventoryDelView(LoginRequiredMixin,DeleteView):

    '''动态主机组删除'''
    model = Inventory
    template_name = 'user/delete.html'
    success_url = reverse_lazy('ansible_task:inventory_list')
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(InventoryDelView,self).get_context_data()
        context['cancel'] = reverse_lazy('ansible_task:inventory_list')
        context['title'] = '删除动态主机组'
        return  context


class GetInverntoryHost(LoginRequiredMixin,View):
    '''获取自定义主机列表,运行模块时选择自定义主机调用'''
    def post(self,request):
        group_ids = request.POST.getlist('hostGroup')
        hosts = GenResource().gen_host_dict(group_ids)
        print(hosts)
        return JsonResponse({'status':True,'hosts':hosts})

class RunModule(LoginRequiredMixin,View):
    '''模块执行'''
    def get(self,request):
        inventory = Inventory.objects.prefetch_related('hosts')
        hosts = Hosts.objects.all()
        remote_ip = request.META['REMOTE_ADDR']
        return render(request,'task/run_module.html',locals())

#运行日志查看，run_log.html
class AnsibleLogView(LoginRequiredMixin,View):
    def post(self,request):
        start_time = request.POST.get('starttime')
        end_time = request.POST.get('endtime')
        ntime = datetime.strptime(end_time, '%Y-%m-%d') + datetime.timedelta(1)
        end_time = ntime.strftime('%Y-%m-%d')
        log_type = request.POST.get('logType')
        try:
            if log_type =='module':
                records =[]
                ansible_logs = AnsibleOperLog.objects.filter(ctime__gt=start_time,ctime__lt=end_time)
                for log in ansible_logs:
                    record = {
                        'id':log.id,
                        'user':log.user.name,
                        'remote_ip':log.remote_ip,
                        'module':log.module,
                        'args':log.args,
                        'server':log.server,
                        'result':log.result,
                        'ctime':log.ctime,
                    }
                    records.append(record)
                return JsonResponse({'status':True,'records':records})
            elif log_type =='playbook':
                records =[]
                ansible_logs = PlayBookLogs.objects.filter(ctime__gt=start_time,ctime__lt=end_time)
                for log in ansible_logs:
                    record ={
                        'id':log.id,
                        'user':log.user,
                        'remote_ip':log.remote_ip,
                        'name':log.name,
                        'result':log.result,
                        'ctime':log.ctime
                    }
                    records.append(record)
                    return  JsonResponse({'status':True,'records':records})
        except Exception as  e:
            return JsonResponse({'status':False,'msg':e})

    def get(self,request):
        module_log_id = request.GET.get('module_log_id')
        playbook_log_id = request.GET.get('playbook_log_id')
        if module_log_id:
            module_log = AnsibleOperLog.objects.get(id=module_log_id)
            result = eval(module_log.result)
            return  JsonResponse({'status':True,'data':result})
        elif playbook_log_id:
            playbook_log = PlayBookLogs.objects.get(id=playbook_log_id)
            result = eval(playbook_log.result)
            return JsonResponse({'status':True,'data':result})
        else:
            module_log_info = AnsibleOperLog.objects.select_related('user').all()
            playbook_log_info = PlayBookLogs.objects.select_related('user').all()
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1
            p1 = Paginator(module_log_info, 10, request=request)
            p2 = Paginator(playbook_log_info,10,request=request)
            all_module_log = p1.page(page)
            all_playbook_log = p2.page(page)
            return render(request,'task/log.html',locals())

class ModuleLogDel(LoginRequiredMixin,View):
    '''删除module运行日志'''
    def post(self,request):
        try:
            pk = request.POST.get('pk')
            if pk:
                AnsibleOperLog.objects.filter(id=pk).delete()
                return HttpResponse(json.dumps({'status': True, 'msg': '删除成功'}))
        except Exception as e:
            print(e)

class PlayBookLogDel(LoginRequiredMixin,View):
    '''删除playbook日志'''
    def post(self,request):
        try:
            pk = request.POST.get('pk')
            if pk:
                PlayBookLogs.objects.filter(id=pk).delete()
                return HttpResponse(json.dumps({'status': True, 'msg': '删除成功'}))
        except Exception as e:
            print(e)

#添加playbook
class PlaybooksAdd(LoginRequiredMixin,View):
    raise_exception = True
    def post(self,request):
        if request.is_ajax():
            name = request.POST.get('name')
            content = request.POST.get('content')
            desc = request.POST.get('desc')
            try:
                t = datetime.now()
                upload_path = 'playbook/{0}/{1}/{2}'.format(str(t.year), str(t.month), str(t.day))
                file = upload_path + '/' + name
                PlayBooks.objects.create(
                    name=name,file=file,user=request.user,desc=desc,content=content
                )

                file_path = os.path.join(settings.MEDIA_ROOT,upload_path)
                if not os.path.exists(file_path):
                    mkdir_p(file_path)
                with open('{0}/{1}'.format(file_path, name), 'w') as f:
                        f.write(content)

                return  JsonResponse({"status":True,"msg":"添加完成"})
            except Exception as e:
                return HttpResponse(json.dumps({"status":False,"msg":e}))

#上传playbook
class PlayBookUpload(LoginRequiredMixin,View):
    def post(self,request):
        if request.is_ajax():
            file = request.FILES.get('playbook_file')
            name = request.POST.get('name')
            if file:
                playbook = PlayBooks.objects.create(name = file.name,file=file,user=request.user)
                content = ''
                with open(playbook.file.path,'r') as f:
                    for line in f.readlines():
                        content = content +line
                playbook.content = content
                playbook.save()
                return JsonResponse({'status':True,'msg':'添加文件完成'})
            elif name:
                desc = request.POST.get('desc')
                obj = PlayBooks.objects.select_related('user').get(name=name)
                obj.desc = desc
                obj.save()
                return JsonResponse({'status':True,'msg':'上传文件完成'})

#playbook列表
class PlayBookList(LoginRequiredMixin,View):
    def get(self,request):
        playbooks = PlayBooks.objects.select_related('user').all()
        inventory = Inventory.objects.prefetch_related('hosts')
        remote_ip = request.META['REMOTE_ADDR']
        return render(request,'task/playbook.html',locals())

#playbook修改
class PlayBookDetail(LoginRequiredMixin,View):
    def get(self,request,pk):
        playbook = PlayBooks.objects.select_related('user').get(id=pk)
        obj = {
            'name':playbook.name,
            'desc':playbook.desc,
            'content':playbook.content
        }
        return JsonResponse({'status':True,'data':obj})
    def post(self,request,pk):
        playbook = PlayBooks.objects.select_related('user').get(id=pk)
        try:
            content = request.POST.get('content')
            file = playbook.file.path
            with open(file,'w') as f:
                f.write(content)
            PlayBooks.objects.select_related('user').filter(id=pk).update(
                name = request.POST.get('name'),
                content = content,
                desc = request.POST.get('desc')
            )
            return  JsonResponse({'status':True,'msg':'更新完成'})
        except Exception as e:
            return JsonResponse({'status':False,'msg':e})

#运行playbook
class PlayBookRun(LoginRequiredMixin,View):
    def get(self,request,pk):
        playbook = PlayBooks.objects.select_related('user').get(id=pk)
        content = playbook.content
        return JsonResponse({'status':True,'content':content})

#删除playbook
class PlayBookDel(LoginRequiredMixin,View):
    def post(self,request,pk):
        playbook = PlayBooks.objects.get(id=pk)
        os.remove(playbook.file.path)
        playbook.delete()
        return JsonResponse({'status':True,'msg':'删除成功'})

#检查是否重名
def check_name(request):
    playbook_name = request.GET.get('playbook_name')
    role_name = request.GET.get('role_name')
    playbook = PlayBooks.objects.filter(name=playbook_name).exists()
    role = AnsibleRole.objects.filter(name=role_name).exists()
    if playbook or role:
        return JsonResponse({'status': False, 'msg': '同名文件已存在！'})
    else:
        return JsonResponse({'status': True})

#role列表
class RoleList(LoginRequiredMixin,View):
    def get(self,request):
        inventory = Inventory.objects.prefetch_related('hosts')
        roles = AnsibleRole.objects.select_related('user').all()
        return render(request,'task/role.html',locals())
    def post(self,request):
        file = request.FILES.get('role_file')
        name = request.POST.get('name')
        if file:
            AnsibleRole.objects.create(name = file.name.split('.zip')[0],file=file,user=request.user)
        elif name:
            obj = AnsibleRole.objects.select_related('user').get(name=name.split('.zip')[0])
            obj.desc = request.POST.get('desc')
            obj.save()
            z = zipfile.ZipFile(obj.file.path,'r')
            try:
                z.extractall(path=settings.ANSIBLE_ROLE_PATH)
            finally:
                z.close()
                os.remove(obj.file.path)
        return  JsonResponse({'status':True,'msg':'上传成功'})


#RoleDetail，返回role_detail.html
class RoleDetail(LoginRequiredMixin,View):
    def get(self,request,pk):
        name = request.POST.get('name')
        p_name = request.POST.get('p_name')
        return  render(request,'task/role_detail.html',locals())
    def post(self,request,pk):
        name = request.POST.get('name')
        p_name = request.POST.get('p_name')
        if name and p_name:
            nodes = []
            path_names = os.listdir(os.path.join(p_name, name))
            path_names.sort()
            for path_name in path_names:
                if not path_name.endswith('retry'):
                    node = {'name': path_name, 'p_name': p_name + '/' + name}
                    if os.path.isdir(os.path.join(p_name, name, path_name)):
                        node['isParent'] = True
                    else:
                        node['isParent'] = False
                    nodes.append(node)
            return HttpResponse(json.dumps(nodes))
        else:
            role_name = AnsibleRole.objects.get(id=pk).name
            node = {'name': role_name, 'isParent': True, 'p_name': settings.ANSIBLE_ROLE_PATH}
            return HttpResponse(json.dumps(node))

#添加role，role_add.html
class RoleAdd(LoginRequiredMixin,View):
    def get(self,request):
        name = request.GET.get('name')
        desc = request.GET.get('desc')
        root_path = settings.ANSIBLE_ROLE_PATH
        AnsibleRole.objects.select_related('user').create(
            name=name,
            file='{}/{}'.format('roles',name),
            user = request.user,
            desc = desc
        )
        return render(request,'task/role_add.html',locals())

#获取文件内容
class GetFileContent(LoginRequiredMixin,View):
    def post(self,request):
        if request.is_ajax():
            p_name = request.POST.get('p_name')
            name = request.POST.get('name')
            file = os.path.join(p_name, name)
            if os.path.exists(file):
                content = ''
                with open(file, 'r') as f:
                    for line in f.readlines():
                        content = content + line

                relative_path = p_name.split('{}/{}/'.format(settings.MEDIA_ROOT, 'roles'))[-1] + '/' + name
                return JsonResponse({'status': True, 'content': content, 'relative_path': relative_path})
            else:
                return JsonResponse({'status': False, 'msg': 'No such file or dictionary!'})

#更新role
class RoleUpdate(LoginRequiredMixin,View):
    def post(self,request):
        if request.is_ajax():
            content = request.POST.get('content')
            relative_path = request.POST.get('relative_path')
            p_name = request.POST.get('p_name')
            name = request.POST.get('name')

            try:
                if relative_path:
                    with open(os.path.join(settings.ANSIBLE_ROLE_PATH, relative_path), 'w') as f:
                        f.write(content)
                    return JsonResponse({'status': True, 'msg': '修改完成！'})
                elif p_name and name:
                    if not os.path.exists(p_name):
                        os.makedirs(p_name)
                    with open(os.path.join(p_name, name), 'w') as f:
                        f.write(content)
                    return JsonResponse({'status': True, 'msg': '保存完成！'})
            except Exception as e:
                return JsonResponse({'status': True, 'msg': '操作失败！：{}'.format(e)})

#删除role
class RoleDel(LoginRequiredMixin,View):
    def post(self,request,pk):
        role = AnsibleRole.objects.get(id=pk)
        try:
            shutil.rmtree(os.path.join(settings.ANSIBLE_ROLE_PATH,role.name))
            return  JsonResponse({'status':True,'msg':'删除成功'})
        except Exception as e:
            return JsonResponse({'status':False,'msg':e})
        finally:
            role.delete()


#删除role路径
class PathDel(LoginRequiredMixin,View):
    def post(self,request):
        if request.is_ajax():
            name = request.POST.get('name')
            p_name = request.POST.get('p_name')
            path = os.path.join(p_name, name)
            try:
                if os.path.exists(path):
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                return JsonResponse({'status': True, 'msg': '删除成功！'})
            except Exception as e:
                return JsonResponse({'status': False, 'msg': '删除失败！{}'.format(e)})

#创建role路径
class PathCreate(LoginRequiredMixin,View):
    def post(self,request):
        if request.is_ajax():
            name = request.POST.get('name')
            p_name = request.POST.get('p_name')
            is_parent = request.POST.get('isParent')
            new_name = request.POST.get('new_name')
            path = os.path.join(p_name, name)
            new_path = os.path.join(p_name, new_name)
            try:
                if not os.path.exists(path) and not os.path.exists(new_path):
                    if is_parent == 'true':
                        os.makedirs(new_path)
                    else:
                        open(new_path, 'w').close()
                    return JsonResponse({'status': True, 'msg': '添加成功！'})
                elif os.path.exists(path) and not os.path.exists(new_path):
                    os.rename(path, new_path)
                    return JsonResponse({'status': True, 'msg': '修改成功！'})
            except Exception as e:
                return JsonResponse({'status': False, 'msg': '操作失败！{}'.format(e)})

