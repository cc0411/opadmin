# -*- coding: utf-8 -*-
import paramiko
import socket
from channels.generic.websockets import WebsocketConsumer
try:
    import simplejson as json
except ImportError:
    import json
from .interactive import interactive_shell, SshTerminalThread, InterActiveShellThread
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_text as smart_unicode
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from .models import AuditLog
from asset.models import Hosts
import time
from users.models import UserProfile,HostPermission
from django.utils.timezone import now
import os
from channels import Group
import traceback
from .utils import WebsocketAuth, get_redis_instance
import logging
import uuid
from utils import  crypt_password
from six import string_types as basestring
import ast
try:
    unicode
except NameError:
    unicode = str

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
logger = logging.getLogger(__name__)

c = crypt_password.AESCipher
class Webterminal(WebsocketConsumer, WebsocketAuth):

    ssh = paramiko.SSHClient()
    http_user = True
    channel_session = True
    channel_session_user = True

    def connect(self, message, **kwargs):
        self.message.reply_channel.send({"accept": True})
        print('已连接')
        if not self.authenticate:
            self.message.reply_channel.send({"text": json.dumps(
                {'status': False, 'message': '你必须登录!'})}, immediately=True)
            self.message.reply_channel.send({"accept": False})

    def disconnect(self, message, **kwargs):
        # close threading
        self.closessh()

        self.message.reply_channel.send({"accept": False})

        audit_log = AuditLog.objects.get(user=UserProfile.objects.get(
            username=self.message.user), channel=self.message.reply_channel.name)
        audit_log.is_finished = True
        audit_log.end_time = now()
        audit_log.save()
        self.close()

    @property
    def queue(self):
        queue = get_redis_instance()
        channel = queue.pubsub()
        return queue

    def closessh(self):
        # close threading
        self.queue.publish(self.message.reply_channel.name,
                           json.dumps(['close']))

    def receive(self, text=None, bytes=None, **kwargs):
        print(text)
        try:
            if text:
                data = json.loads(text)
                begin_time = time.time()
                if isinstance(data, list) and data[0] == 'ip' and len(data) == 5:
                    ip = data[1]
                    width = data[2]
                    height = data[3]
                    id = data[4]
                    self.ssh.set_missing_host_key_policy(
                        paramiko.AutoAddPolicy())
                    try:
                        data = Hosts.objects.get(wip=ip)
                        port = data.user.ssh_port
                        method = data.user.auth_method
                        username = data.user.username
                        if method == 'ssh-password':
                            p = data.user.password
                            password = c().decrypt(p)
                        else:
                            key = data.user.key
                    except ObjectDoesNotExist:
                        self.message.reply_channel.send(
                            {"bytes": '\033[1;3;31mConnect to server! Server ip doesn\'t exist!\033[0m'}, immediately=True)
                        self.message.reply_channel.send({"accept": False})
                        logger.error(
                            "Connect to server! Server ip {0} doesn\'t exist!".format(ip))
                    try:
                        if method == 'ssh-password':
                            self.ssh.connect(
                                ip, port=port, username=username, password=password, timeout=3)
                        else:
                            private_key = StringIO.StringIO(key)
                            if 'RSA' in key:
                                private_key = paramiko.RSAKey.from_private_key(
                                    private_key)
                            elif 'DSA' in key:
                                private_key = paramiko.DSSKey.from_private_key(
                                    private_key)
                            elif 'EC' in key:
                                private_key = paramiko.ECDSAKey.from_private_key(
                                    private_key)
                            elif 'OPENSSH' in key:
                                private_key = paramiko.Ed25519Key.from_private_key(
                                    private_key)
                            else:
                                self.message.reply_channel.send({"bytes":
                                                                 '\033[1;3;31munknown or unsupported key type, only support rsa dsa ed25519 ecdsa key type\033[0m'}, immediately=True)
                                self.message.reply_channel.send(
                                    {"accept": False})
                                logger.error(
                                    "unknown or unsupported key type, only support rsa dsa ed25519 ecdsa key type!")
                            self.ssh.connect(
                                ip, port=port, username=username, pkey=private_key, timeout=3)
                        # when connect server sucess record log
                        audit_log = AuditLog.objects.create(user=UserProfile.objects.get(
                            username=self.message.user), server=data, channel=self.message.reply_channel.name, width=width, height=height)
                        audit_log.save()
                    except socket.timeout:
                        self.message.reply_channel.send(
                            {"bytes": '\033[1;3;31mConnect to server time out\033[0m'}, immediately=True)
                        logger.error(
                            "Connect to server {0} time out!".format(ip))
                        self.message.reply_channel.send({"accept": False})
                        return
                    except Exception as e:
                        self.message.reply_channel.send(
                            {"bytes": '\033[1;3;31mCan not connect to server: {0}\033[0m'.format(e)}, immediately=True)
                        self.message.reply_channel.send({"accept": False})
                        logger.error(
                            "Can not connect to server {0}: {1}".format(ip, e))
                        return

                    chan = self.ssh.invoke_shell(
                        width=width, height=height, term='xterm')

                    # open a new threading to handle ssh to avoid global variable bug
                    sshterminal = SshTerminalThread(self.message, chan)
                    sshterminal.setDaemon = True
                    sshterminal.start()

                    directory_date_time = now()
                    log_name = os.path.join('{0}-{1}-{2}'.format(directory_date_time.year,
                                                                 directory_date_time.month, directory_date_time.day), '{0}'.format(audit_log.log))

                    # open ssh terminal
                    interactivessh = InterActiveShellThread(
                        chan, self.message.reply_channel.name, log_name=log_name, width=width, height=height)
                    interactivessh.setDaemon = True
                    interactivessh.start()

                elif isinstance(data, list) and data[0] in ['stdin', 'stdout']:
                    self.queue.publish(
                        self.message.reply_channel.name, json.loads(text)[1])
                elif isinstance(data, list) and data[0] == u'set_size':
                    self.queue.publish(self.message.reply_channel.name, text)
                elif isinstance(data, list) and data[0] == u'close':
                    self.disconnect(self.message)
                    return
                else:
                    self.queue.publish(self.message.reply_channel.name, text)

            elif bytes:
                self.queue.publish(
                    self.message.reply_channel.name, bytes)
        except socket.error:
            audit_log = AuditLog.objects.get(user=UserProfile.objects.get(
                username=self.message.user), channel=self.message.reply_channel.name)
            audit_log.is_finished = True
            audit_log.end_time = now()
            audit_log.save()
            self.closessh()
            self.close()
        except ValueError:
            self.queue.publish(
                self.message.reply_channel.name, smart_unicode(text))
        except Exception as e:
            logger.error(traceback.print_exc())
            self.closessh()
            self.close()

class SshTerminalMonitor(WebsocketConsumer, WebsocketAuth):

    http_user = True
    http_user_and_session = True
    channel_session = True
    channel_session_user = True
    def connect(self, message,channel):
        """
        User authenticate and detect user has permission to monitor user ssh action!
        """
        if not self.authenticate:
            self.message.reply_channel.send({"text": json.dumps(
                {'status': False, 'message': 'You must login to the system!'})}, immediately=True)
            self.message.reply_channel.send({"accept": False})
        if not self.haspermission('common.can_monitor_serverinfo'):
            self.message.reply_channel.send({"text": json.dumps(
                {'status': False, 'message': 'You have not permission to monitor user ssh action!'})}, immediately=True)
            self.message.reply_channel.send({"accept": False})
        self.message.reply_channel.send({"accept": True})
        Group(channel).add(self.message.reply_channel.name)

    def disconnect(self, message, channel,**kwargs):
        Group(channel).discard(self.message.reply_channel.name)
        self.message.reply_channel.send({"accept": False})
        self.close()

    def receive(self, text=None, bytes=None, **kwargs):
        pass

class BatchCommandExecute(WebsocketConsumer, WebsocketAuth):
    http_user = True
    http_user_and_session = True
    channel_session = True
    channel_session_user = True
    ssh = paramiko.SSHClient()

    def connect(self, message, **kwargs):
        self.message.reply_channel.send({"accept": True})
        if not self.authenticate:
            self.message.reply_channel.send({"text": json.dumps(
                {'status': False, 'message': 'You must login to the system!'})}, immediately=True)
            self.message.reply_channel.send({"accept": False})

    def disconnect(self, message, **kwargs):
        self.message.reply_channel.send({"accept": False})
        self.close()

    @property
    def queue(self):
        queue = get_redis_instance()
        channel = queue.pubsub()
        return queue

    def receive(self, text=None, bytes=None, **kwargs):
        """
        Protocol
        register terminal id
        ["register", ip, term.cols, term.rows, serverid, element.id]
        stdin data
        ['stdin', data, element.id]
        stdout data
        ['stdout', data, element.id]
        command data
        ["command",  data, selected[i].original.elementid]
        close terminal data
        ["close",  'close', selected[i].original.elementid]
        channel_name data
        ["channel_name","channel_name",elementid]
        disconnect data
        ["disconnect",msg,elementid]
        auth data
        {'status':False,'message':'You must login to the system!'}
        """
        try:
            if text:
                data = json.loads(text)
                logger.debug('receive data {0}'.format(data))
                if len(data) > 0 and isinstance(data, list) and data[0] == 'register':
                    ip = data[1]
                    id = data[4]
                    channel = self.message.reply_channel.name
                    width = data[2]
                    height = data[3]
                    elementid = data[5]
                    elementid = '{0}_{1}'.format(
                        elementid, str(uuid.uuid4()))
                    self.openterminal(ip, id, channel, width,
                                      height, elementid=elementid)
                elif len(data) > 0 and isinstance(data, list) and data[0] == 'command':
                    command = data[1].strip('\n')
                    self.queue.publish(
                        data[2], ['stdin', '{0}\r'.format(command), 'command'])
                elif len(data) > 0 and isinstance(data, list) and data[0] == 'stdin':
                    self.queue.publish(data[2], ['stdin', data[1]])
                elif len(data) > 0 and isinstance(data, list) and data[0] == 'close':
                    self.queue.publish(data[2], ['close'])
        except Exception as e:
            logger.error(traceback.print_exc())
            self.message.reply_channel.send({"text": json.dumps(
                ['stdout', '\033[1;3;31mSome error happend, Please report it to the administrator! Error info:%s \033[0m' % (smart_unicode(e))])}, immediately=True)

    def openterminal(self, ip, id, channel, width, height, elementid=None):
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #try:
        #    HostPermission.objects.get(user__username=self.message.user.username, groups__servers__ip=ip,
        #                           groups__servers__id=id, groups__servers__credential__protocol__contains='ssh')
        #except ObjectDoesNotExist:
        #    self.message.reply_channel.send({"text": json.dumps(
        #        ['stdout', '\033[1;3;31mYou have not permission to connect server {0}!\033[0m'.format(ip), elementid.rsplit('_')[0]])}, immediately=True)
        #    self.message.reply_channel.send({"accept": False})
        #    return
        #except MultipleObjectsReturned:
        #    pass
        try:
            data = Hosts.objects.get(
                wip=ip)
            port = data.user.ssh_port
            method = data.user.auth_method
            username = data.user.username
            if method == 'ssh-password':
                p = data.user.password
                password = c().decrypt(p)
            else:
                key = data.user.key
        except ObjectDoesNotExist:
            self.message.reply_channel.send({"text": json.dumps(
                ['stdout', '\033[1;3;31mConnect to server! Server ip doesn\'t exist!\033[0m', elementid.rsplit('_')[0]])}, immediately=True)
            self.message.reply_channel.send({"accept": False})
        try:
            if method == 'ssh-password':
                self.ssh.connect(ip, port=port, username=username,
                                 password=password, timeout=3)
            else:
                private_key = StringIO.StringIO(key)
                if 'RSA' in key:
                    private_key = paramiko.RSAKey.from_private_key(
                        private_key)
                elif 'DSA' in key:
                    private_key = paramiko.DSSKey.from_private_key(
                        private_key)
                elif 'EC' in key:
                    private_key = paramiko.ECDSAKey.from_private_key(
                        private_key)
                elif 'OPENSSH' in key:
                    private_key = paramiko.Ed25519Key.from_private_key(
                        private_key)
                else:
                    self.message.reply_channel.send({"text": json.dumps(
                        ['stdout', '\033[1;3;31munknown or unsupported key type, only support rsa dsa ed25519 ecdsa key type\033[0m', elementid.rsplit('_')[0]])}, immediately=True)
                    self.message.reply_channel.send({"accept": False})
                self.ssh.connect(
                    ip, port=port, username=username, pkey=private_key, timeout=3)
            # record log
            audit_log = AuditLog.objects.create(user=UserProfile.objects.get(
                username=self.message.user), server=data, channel=elementid, width=width, height=height)
            audit_log.save()
        except socket.timeout:
            self.message.reply_channel.send({"text": json.dumps(
                ['stdout', '\033[1;3;31mConnect to server time out\033[0m', elementid.rsplit('_')[0]])}, immediately=True)
            self.message.reply_channel.send({"accept": False})
            return
        except Exception as e:
            self.message.reply_channel.send({"text": json.dumps(
                ['stdout', '\033[1;3;31mCan not connect to server: {0}\033[0m'.format(e), elementid.rsplit('_')[0]])}, immediately=True)
            self.message.reply_channel.send({"accept": False})
            return

        # self.ssh.get_pty()
        chan = self.ssh.invoke_shell(
            width=width, height=height, term='xterm')

        # open a new threading to handle ssh to avoid global variable bug
        sshterminal = SshTerminalThread(
            self.message, chan, elementid=elementid)
        sshterminal.setDaemon = True
        sshterminal.start()

        directory_date_time = now()
        log_name = os.path.join('{0}-{1}-{2}'.format(directory_date_time.year,
                                                     directory_date_time.month, directory_date_time.day), '{0}'.format(audit_log.log))

        interactivessh = InterActiveShellThread(
            chan, self.message.reply_channel.name, log_name=log_name, width=width, height=height, elementid=elementid)
        interactivessh.setDaemon = True
        interactivessh.start()
        self.message.reply_channel.send({"text": json.dumps(
            ['channel_name', elementid.rsplit('_')[0], elementid.rsplit('_')[0]])}, immediately=True)