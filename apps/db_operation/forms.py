# -*- coding:utf-8 -*-
from django import forms
from .models import DbConfig,DbLogs


class DbConfForm(forms.ModelForm):
    class Meta:
        model = DbConfig
        exclude = ['ctime',]
        widgets = {
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.TextInput(attrs={'class': 'form-control'}),
            'memo': forms.TextInput(attrs={'class': 'form-control'}),
            'server': forms.Select(attrs={'class': 'form-control'}),
        }


