# -*- coding:utf-8 -*-
from kubernetes import client, config
from kubernetes.stream import stream
from .models import K8sHost
# Create a configuration object

class K8sApi:

    def __init__(self,confid):
        self.confid = confid


    def get_client(self):
        baseurl = K8sHost.objects.values('k8s_api').get(id=self.confid)['k8s_api']
        token = str(K8sHost.objects.values('k8s_api_token').get(id=self.confid)['k8s_api_token']).strip()
        aConfiguration = client.Configuration()
        aConfiguration.host = baseurl
        aConfiguration.verify_ssl = False
        aConfiguration.api_key = {"authorization": "Bearer " + token}
        aApiClient = client.ApiClient (aConfiguration)
        v1 = client.CoreV1Api(aApiClient)
        return v1


    def get_podlist(self,namespace):
        client_v1 = self.get_client()
        ret_pod = client_v1.list_namespaced_pod(namespace=namespace)
        return ret_pod


    def get_namespacelist(self):
        client_v1 = self.get_client()
        ret_namespace = client_v1.list_namespace()
        return ret_namespace


    def test_pods_connect(self,podname,namespace,command,container=None):
        client_v1 = self.get_client()
        if stream(client_v1.connect_get_namespaced_pod_exec, podname, namespace, command=command,
                container=container,
                stderr=True, stdin=False,
                stdout=True, tty=False):
            return True
        else:
            return False


    def get_pods_exec(self,podname,namespace,command,container=None):
        client_v1 = self.get_client()
        if container:
            rest = stream(client_v1.connect_get_namespaced_pod_exec, podname, namespace, command=command,
                          container=container,
                          stderr=True, stdin=False,
                          stdout=True, tty=False)
        else:
            rest = stream(client_v1.connect_get_namespaced_pod_exec, podname, namespace, command=command,
                           stderr=True, stdin=False,
                           stdout=True, tty=False)
        return rest