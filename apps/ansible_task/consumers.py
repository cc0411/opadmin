# -*- coding: utf-8 -*-
import json
from django.conf import settings
from asset.models import Hosts
from webterminal.utils import get_redis_instance
from .tasks import playbook_record,module_record
from .models import PlayBooks
from django.contrib.auth import get_user_model
from .utils.redis_ops import RedisOps
from .utils.ansible_api_v2 import ANSRunner
from .utils.gen_resource import GenResource
from channels.generic.websockets import WebsocketConsumer
User = get_user_model()


class AnsModuleConsumer(WebsocketConsumer):
    http_user = True
    channel_session = True
    channel_session_user = True
    def __init__(self, *args, **kwargs):
        super(AnsModuleConsumer, self).__init__(*args, **kwargs)
        self.ans_info = None
    def get_redis(self):
        redis = RedisOps(settings.REDIS_HOST, settings.REDIS_PORT, 4)
        return redis
    @property
    def queue(self):
        queue = get_redis_instance()
        channel = queue.pubsub()
        return queue
    def connect(self ,message, **kwargs):
        self.message.reply_channel.send({"accept": True})
        print('已连接')

    def receive(self, text=None, bytes=None, **kwargs):
        print('已收到数据')
        print(text)
        if text:
            self.ans_info = json.loads(text)
            group_ids = self.ans_info['hostGroup']
            host_ids = self.ans_info['ans_group_hosts']
            selected_module_name = self.ans_info['ansibleModule']
            custom_model_name = self.ans_info.get('customModule', None)
            module_args = self.ans_info['ansibleModuleArgs']

            self.run_model(group_ids, host_ids, selected_module_name, custom_model_name, module_args)
        elif bytes:
            self.queue.publish(
                self.message.reply_channel.name, bytes)
    def disconnect(self,message, **kwargs):
        self.message.reply_channel.send({"accept": False})
    def run_model(self, group_ids, host_ids, selected_module_name, custom_model_name, module_args):
        gen_resource = GenResource()

        if group_ids == ['custom'] or group_ids == ['all']:
            resource = gen_resource.gen_host_list(host_ids)
        else:
            resource = gen_resource.gen_group_dict(group_ids)

        host_list = [Hosts.objects.get(id=host_id).nip for host_id in host_ids]

        module_name = selected_module_name if selected_module_name != 'custom' else custom_model_name

        unique_key = '{}.{}.{}'.format(host_ids, module_name, module_args)


        if self.get_redis().get(unique_key):
            self.message.reply_channel.send(
                {"bytes": '<code style="color: #FF0000">\n有相同的任务正在进行！请稍后重试！\n</code>'}, immediately=True)
            #    self.send('<code style="color: #FF0000">\n有相同的任务正在进行！请稍后重试！\n</code>', close=True)
        else:
            try:
                self.get_redis().set(unique_key, 1)
                ans = ANSRunner(resource, become='yes', become_method='sudo', become_user='root', sock=self)
                ans.run_module(host_list=host_list, module_name=module_name, module_args=module_args)

                module_record.delay(ans_user=User.objects.get(id=self.ans_info['run_user']),
                                    ans_remote_ip=self.ans_info['remote_ip'],
                                    ans_module=module_name,
                                    ans_args=module_args,
                                    ans_server=host_list, ans_result=ans.get_module_results)
            except Exception as e:
                print(e)
                self.message.reply_channel.send(
                    {"bytes": '<code style="color: #FF0000">\nansible执行模块出错：{}\n</code>'.format(str(e))}, immediately=True)
            finally:
                self.get_redis().delete(unique_key)
                self.close()


class AnsPlaybookConsumer(WebsocketConsumer):
    http_user = True
    channel_session = True
    channel_session_user = True
    def __init__(self, *args, **kwargs):
        super(AnsPlaybookConsumer, self).__init__(*args, **kwargs)
        self.ans_info = None
    def get_redis(self):
        redis = RedisOps(settings.REDIS_HOST, settings.REDIS_PORT, 4)
        return redis
    def connect(self,message, **kwargs):
        self.message.reply_channel.send({"accept": True})


    def receive(self, text=None, bytes=None, **kwargs):
        self.ans_info = json.loads(text)

        group_ids = self.ans_info['group_ids']
        playbook_id = self.ans_info['playbook_id']

        self.run_playbook(group_ids, playbook_id)

    def disconnect(self,message, **kwargs):
        self.message.reply_channel.send({"accept": False})

    def run_playbook(self, group_ids, playbook_id):
        playbook = PlayBooks.objects.select_related('user').get(id=playbook_id)
        unique_key = '{}.{}'.format(playbook.name, group_ids)

        if self.get_redis().get(unique_key):
            self.message.reply_channel.send(
                {"bytes": '<code style="color: #FF0000">\n有相同的任务正在进行！请稍后重试！\n</code>'}, immediately=True)
        else:
            try:
                self.get_redis().set(unique_key, 1)
                resource = GenResource().gen_group_dict(group_ids)

                ans = ANSRunner(resource, sock=self)
                ans.run_playbook(playbook.file.path)

                playbook_record.delay(
                    playbook_user=User.objects.get(id=self.ans_info['run_user']),
                    playbook_remote_ip=self.ans_info['remote_ip'],
                    playbook_name=playbook.name,
                    playbook_result=ans.get_playbook_results
                )
            except Exception as e:
                self.message.reply_channel.send(
                    {"bytes": '<code style="color: #FF0000">\nansible执行模块出错：{}\n</code>'.format(str(e))},
                    immediately=True)
            finally:
                self.get_redis().delete(unique_key)
                self.close()
