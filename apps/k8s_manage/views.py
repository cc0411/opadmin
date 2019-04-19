from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,render_to_response
from django.contrib.auth.decorators import login_required

# Create your views here.

import json
from django.http import HttpResponse
from .k8s_api import K8sApi
from .models import K8sHost

def getnamespacelist(request):
    if request.method == 'GET':
        k8s_apiport = str(request.GET.get('k8s_apiport',None)).strip()
        message = []
        if k8s_apiport:
            k8s_client = K8sApi(confid=int(k8s_apiport))
            namespaces_list = k8s_client.get_namespacelist()
            for item in namespaces_list.items:
                message.append(item.metadata.name)
        return HttpResponse (json.dumps({'message': message}, ensure_ascii=False),
                      content_type="application/json,charset=utf-8")
    else:
        return HttpResponse (json.dumps ({'message': "不允许POST请求"}, ensure_ascii=False),
                             content_type="application/json,charset=utf-8")


def getpodlist(request):
    if request.method == "POST":
        messages = ''
        k8s_apiport = str(request.POST.get('k8s_apiport',None)).strip()
        namespace = str(request.POST.get('k8s_namespaces',None)).strip()
        if k8s_apiport and namespace:
            k8s_client = K8sApi(confid=int(k8s_apiport))
            pods_list = k8s_client.get_podlist(namespace=namespace)
            for items in pods_list.items:
                pod_name = items.metadata.name
                pod_namespace = items.metadata.namespace
                pod_creatime = items.metadata.creation_timestamp
                host_ip = items.status.host_ip
                pod_ip = items.status.pod_ip
                messages += '''
                <tr class="grid-item">
                <td class="action-checkbox">
                <a href="/k8sapp/connectpod?k8s_namespaces=%s&k8s_apiport=%s&k8s_pod=%s" target="_blank">
                <img src="/static/icons/ssh.png"/></a>
                </td><td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                </tr>''' %(pod_namespace,k8s_apiport,pod_name,pod_name,pod_ip,host_ip,pod_namespace,pod_creatime)
        return HttpResponse(json.dumps({'message': messages}, ensure_ascii=False),
                         content_type="application/json,charset=utf-8")

    else:
        return HttpResponse(json.dumps({'message': "不允许GET请求"}, ensure_ascii=False),
                         content_type="application/json,charset=utf-8")


@login_required()
def connectpod(request):
    if request.method == "GET":
        namespace = str(request.GET.get ('k8s_namespaces', None)).strip()
        k8s_apiport = str(request.GET.get('k8s_apiport', None)).strip()
        pod_name = str(request.GET.get ('k8s_pod', None)).strip()
        token = str(K8sHost.objects.values ('k8s_ws_token').get(id=k8s_apiport)['k8s_ws_token']).strip()
        k8s_url = K8sHost.objects.values('k8s_ws').get(id=k8s_apiport)['k8s_ws']
        return render_to_response ('xtem_pod.html', {'status': 'ok', 'namespace': namespace, 'k8s_url': k8s_url,
                                                     'pod_name': pod_name,'token':token})
    else:
        return render_to_response ('xtem_pod.html', {'status': 'error'})

def podexec(request):
    if request.method == "POST":
        namespace = str(request.POST.get('k8s_namespaces', None)).strip()
        k8s_apiport = str(request.POST.get('k8s_apiport', None)).strip()
        pod_name = str(request.POST.get('k8s_pod',None)).strip()
        command = str(request.POST.get('command', None)).strip ()
        k8s_client = K8sApi(confid=int(k8s_apiport))
        rest = k8s_client.get_pods_exec(podname=pod_name,namespace=namespace,command=command)
    else:
        rest = '不允许除POST之外的任何访问.'
    return HttpResponse(json.dumps({'message': rest}, ensure_ascii=False),content_type="application/json,charset=utf-8")