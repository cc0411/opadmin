# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from opadmin.settings import MEDIA_URL
from django.views.generic import TemplateView,View,ListView
import  json
import re
import uuid
from .encrypt import PyCrypt
from  users.models import HostPermission
from asset.models import HostGroup,Hosts
import subprocess as commands
from django.utils.timezone import now
from .utils import get_redis_instance
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.detail import DetailView
from .models import AuditLog,CommandLog
from pure_pagination import PageNotAnInteger,EmptyPage,Paginator
import logging
logger = logging.getLogger(__name__)
class AuditLogList(LoginRequiredMixin,ListView):
    '''审计日志列表'''
    model = AuditLog
    template_name = 'webssh/logslist.html'
    context_object_name = 'all_logs'
    queryset = AuditLog.objects.all()
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
        context = super(AuditLogList, self).get_context_data()
        context['title'] = '审计日志列表'
        return context

class SshLogPlay(LoginRequiredMixin,DetailView):
    '''日志播放'''
    model = AuditLog
    template_name = 'webssh/sshlogplay.html'
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(SshLogPlay,self).get_context_data(**kwargs)
        objects = kwargs['object']
        context['logpath'] = '{0}{1}-{2}-{3}/{4}'.format(
            MEDIA_URL, objects.start_time.year, objects.start_time.month, objects.start_time.day, objects.log)
        return  context

class SshTerminalMonitor(LoginRequiredMixin,DetailView):
    '''ssh日志监控'''
    model = AuditLog
    template_name = 'webssh/sshlogmonitor.html'
    raise_exception = True

class BatchCommandExecute(LoginRequiredMixin,TemplateView):
    '''批量命令'''
    template_name = 'webssh/batchcommandexecute.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(BatchCommandExecute, self).get_context_data(**kwargs)
        try:
            groups = HostPermission.objects.get(
                user__username=self.request.user.username)
        except ObjectDoesNotExist:
            logger.error('user:{0} have not permission to visit batch command execute page!'.format(
                self.request.user.username))
            return context
        context['server_groups'] = HostGroup.objects.filter(
            name__in=[group.name for group in groups.groups.all()])
        return context

    def post(self, request):
        if request.is_ajax():
            cmd = request.POST.get('cmd', '')
            commandall = commands.getoutput(
                "PATH=$PATH:./:/usr/lib:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin;for dir in $(echo $PATH |sed 's/:/ /g');do ls $dir;done").strip().split('\n')
            commandmatch = []
            for command in commandall:
                match = re.search('^{0}.*'.format(cmd), command)
                if match:
                    commandmatch.append(match.group())
                else:
                    continue
            return JsonResponse({'status': True, 'message': list(set(commandmatch))})
class SshTerminalKill(LoginRequiredMixin,View):
    '''杀掉正在连接的终端'''
    raise_exception = True
    def post(self, request):
        if request.is_ajax():
            channel_name = request.POST.get('channel_name', None)
            try:
                data = AuditLog.objects.get(channel=channel_name)
                if data.is_finished:
                    return JsonResponse({'status': False, 'message': 'Ssh terminal does not exist!'})
                else:
                    data.end_time = now()
                    data.is_finished = True
                    data.save()

                    queue = get_redis_instance()
                    redis_channel = queue.pubsub()
                    if '_' in channel_name:
                        queue.publish(channel_name.rsplit(
                            '_')[0], json.dumps(['close']))
                    else:
                        queue.publish(channel_name, json.dumps(['close']))
                    return JsonResponse({'status': True, 'message': 'Terminal has been killed !'})
            except ObjectDoesNotExist:
                return JsonResponse({'status': False, 'message': 'Request object does not exist!'})

class SshConnect(LoginRequiredMixin,TemplateView):
    '''ssh连接'''
    template_name = 'webssh/ssh.html'
    raise_exception = False
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(SshConnect, self).get_context_data(**kwargs)
        context['ip'] = self.kwargs.get('ip')
        context['serverid'] = self.kwargs.get('serverid')
        return context

class CommandLogList(LoginRequiredMixin,View):
    '''命令历史'''
    raise_exception = True
    def post(self, request):
        if request.is_ajax():
            id = request.POST.get('id', None)
            data = CommandLog.objects.filter(log__id=id)
            if data.count() == 0:
                return JsonResponse({'status': False, 'message': 'Request object not exist!'})
            else:
                return JsonResponse({'status': True, 'message': [{'datetime': i.datetime.strftime('%Y-%m-%d %H:%M:%S'), 'command': i.command} for i in data]})
        else:
            return JsonResponse({'status': False, 'message': 'Method not allowed!'})

class DynamicPassword(LoginRequiredMixin,TemplateView):
    raise_exception = True
    def post(self, request):
        if request.is_ajax():
            serverid = request.POST.get('serverid', None)
            try:
                Hosts.objects.get(id=serverid)
                username = uuid.uuid4().hex[0:5]
                password = uuid.uuid4().hex
                conn = get_redis_instance()
                encrypt = PyCrypt('88aaaf7ffe3c6c0488aaaf7ffe3c6c04')
                key = encrypt.encrypt(content=username + password)
                key = encrypt.md5_crypt(key)
                serverid = encrypt.encrypt(content=serverid)
                password = encrypt.encrypt(content=password)
                request_username = encrypt.encrypt(
                    content=self.request.user.username)
                if isinstance(serverid, bytes):
                    serverid = serverid.decode('utf8')
                if isinstance(request_username, bytes):
                    request_username = request_username.decode('utf8')
                conn.set(key, '{0}_{1}'.format(serverid, request_username))
                conn.set(username, password)
                conn.expire(key, 60)
                conn.expire(username, 60)
                if isinstance(password, bytes):
                    password = password.decode('utf8')
                return JsonResponse({'status': True, 'message': {'username': username, 'password': password}})
            except ObjectDoesNotExist:
                return JsonResponse({'status': False, 'message': 'Request object does not exist!'})

class FilemanageView(LoginRequiredMixin,TemplateView):
    '''文件管理'''
    template_name = 'webssh/filemanage.html'
    raise_exception = False
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(FilemanageView, self).get_context_data(**kwargs)
        context['ip'] = self.kwargs.get('ip')
        context['serverid'] = self.kwargs.get('serverid')
        return context