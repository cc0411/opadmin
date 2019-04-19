# -*- coding: utf-8 -*-
from asset.models import Hosts
from ansible_task.models import Inventory
from utils import crypt_password
c = crypt_password.AESCipher

class GenResource:
    @staticmethod
    def gen_host_list(host_ids):
        """
        生成格式为：[{"ip": "10.0.0.0", "port": "22", "username": "test", "password": "pass"}, ...]
        :return:
        """
        host_list = []
        for host_id in host_ids:
            host = {}
            host_obj = Hosts.objects.get(id=host_id)
            host['ip'] = host_obj.nip
            host['port'] = host_obj.user.ssh_port
            host['username'] = host_obj.user.username
            p = host_obj.user.password
            host['password'] = c().decrypt(p)
            if host_obj.host_vars:
                host_vars = eval(host_obj.host_vars)
                for k, v in host_vars.items():
                    host[k] = v
            host_list.append(host)
        return host_list

    def gen_group_dict(self, group_ids):
        """
        生成格式为:
        {
                "group1": {
                    "hosts": [{"ip": "10.0.0.0", "port": "22", "username": "test", "password": "pass"}, ...],
                    "group_vars": {"var1": value1, "var2": value2, ...}
                }
            }
        :return:
        """
        resource = {}
        for group_id in group_ids:
            group_values = {}
            group_obj = Inventory.objects.prefetch_related('hosts').get(id=group_id)
            host_ids = [host.id for host in group_obj.hosts.all()]
            group_values['hosts'] = self.gen_host_list(host_ids)
            if group_obj.vars:
                group_values['group_vars'] = eval(group_obj.vars)
            resource[group_obj.groupname] = group_values
        return resource

    @staticmethod
    def gen_host_dict(group_ids):
        """
        生成所选主机组内的主机地址, 生成格式是[{'host_id': host.id, 'host_ip': host.ip}, {...}]
        :return:
        """
        hosts_temp = []
        for group_id in group_ids:
            host_list = Inventory.objects.prefetch_related('hosts').get(id=group_id).hosts.all()
            host_d = [{'host_id': host.id, 'host_ip': host.nip} for host in host_list]
            hosts_temp.extend(host_d)

        hosts = []
        for i in hosts_temp:
            if i not in hosts:
                hosts.append(i)

        return hosts
