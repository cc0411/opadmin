# -*- coding:utf-8 -*-
from django import  forms
from .models import RepoConfig

class RepoForm(forms.ModelForm):
    class Meta:
        model = RepoConfig
        exclude = ['ctime']
        widgets = {
            'repo_name': forms.TextInput(attrs={'class': 'form-control'}),
            'repo_type': forms.Select(attrs={'class': 'form-control'}),
            'repo_user': forms.TextInput(attrs={'class': 'form-control'}),
            'repo_password': forms.TextInput(attrs={'class': 'form-control'}),
            'repo_url': forms.TextInput(attrs={'class': 'form-control'}),
            'repo_model': forms.Select(attrs={'class': 'form-control'}),
        }