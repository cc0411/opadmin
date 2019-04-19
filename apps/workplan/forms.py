# -*- coding: utf-8 -*-

from django import  forms
from .models import CdnLog,OperationLog
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Div,Field


class CdnLogForm(forms.ModelForm):
    class Meta:
        model = CdnLog
        fields = ['gname', 'version','is_full','user','is_flush','cdn_type']
        widgets = {
            'gname': forms.TextInput(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.TextInput(attrs={'class': 'form-control'}),
            'cdn_type': forms.Select(attrs={'class': 'form-control m-d'}),
        }
class OperationLogForm(forms.ModelForm):
    class Meta:
        model = OperationLog
        fields = ['gname', 'version_online','version_updated','user','game_package','game_type','desc','is_new']
        widgets = {
            'gname': forms.TextInput(attrs={'class': 'form-control'}),
            'version_online': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.TextInput(attrs={'class': 'form-control'}),
            'version_updated': forms.TextInput(attrs={'class': 'form-control'}),
            'game_package': forms.TextInput(attrs={'class': 'form-control'}),
            'game_type': forms.Select(attrs={'class': 'form-control m-d'}),
            'is_new': forms.Select(attrs={'class': 'form-control m-d'}),
            'desc': forms.Textarea(attrs={'class': 'form-control'}),
        }