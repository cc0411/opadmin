# -*- coding:utf-8 -*-
from .models import Inventory
from django import forms

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        exclude = ['ctime']
        widgets = {
            'groupname': forms.TextInput(attrs={'class': 'form-control'}),
            'vars': forms.TextInput(attrs={'class': 'form-control'}),
            'memo': forms.TextInput(attrs={'class': 'form-control'}),
            'hosts': forms.SelectMultiple(attrs={'class': 'form-control m-b'}),
        }
