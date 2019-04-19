# -*- coding:utf-8 -*-
from django import  forms
from .models import HostUsers,Hosts,HostGroup,IDC,UserHostPer
class HostForm(forms.ModelForm):
    class Meta:
        model = Hosts
        exclude = ['desc','ctime','utime',]
        widgets = {
            'hostname': forms.TextInput(attrs={'class': 'form-control'}),
            'wip': forms.TextInput(attrs={'class': 'form-control'}),
            'nip': forms.TextInput(attrs={'class': 'form-control'}),
            'instance_id': forms.TextInput(attrs={'class': 'form-control'}),
            'sn': forms.TextInput(attrs={'class': 'form-control'}),
            'cpu_info': forms.TextInput(attrs={'class': 'form-control'}),
            'memory': forms.TextInput(attrs={'class': 'form-control'}),
            'disk': forms.TextInput(attrs={'class': 'form-control'}),
            'server_id': forms.TextInput(attrs={'class': 'form-control'}),
            'game_id': forms.TextInput(attrs={'class': 'form-control'}),
            'os': forms.TextInput(attrs={'class': 'form-control'}),
            'server_type': forms.Select(attrs={'class': 'form-control m-b'}),
            'status': forms.Select(attrs={'class': 'form-control m-b'}),
            'user': forms.Select(attrs={'class': 'form-control m-b'}),
        }
        help_texts = {
            'hostname': '名字唯一,主机名这里请不要写IP',
            'user': '创建资产前请先创建远程主机账户'
        }

class HostUsersForm(forms.ModelForm):
    class Meta:
        model = HostUsers
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'ssh_port': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'key': forms.Textarea(attrs={'class': 'form-control'}),
            'auth_method': forms.Select(attrs={'class': 'form-control m-d'}),
        }

class  UserHostPerForm(forms.ModelForm):
    host_groups = forms.ModelMultipleChoiceField(required=False,label='管理的主机组',queryset=HostGroup.objects.all(),widget=forms.SelectMultiple(attrs={'class':'form-control select2','style':'width: 100%;'}))
    bind_hosts = forms.ModelMultipleChoiceField(required=False,label='管理的主机',queryset=Hosts.objects.all(),widget=forms.SelectMultiple(attrs={'class':'form-control select2','style':'width: 100%;'}))
    class Meta:
        model =UserHostPer
        exclude = ['ctime','utime']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control m-b'}),
        }


class HostGroupForm(forms.ModelForm):
    class Meta:
        model = HostGroup
        exclude = ['ctime',]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'host': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
class IdcForm(forms.ModelForm):
    class Meta:
        model = IDC
        exclude = ['ctime', ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'servers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
