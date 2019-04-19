# -*- coding:utf-8 -*-

from django import  forms
from django.utils.safestring import mark_safe
from users.models import Role,Menu,Permission
from .base import BootStrapModelForm
ICON_LIST = [
    ['fa-lock', '<i aria-hidden="true" class="fa fa-lock"></i>'],
    ['fa-home', '<i aria-hidden="true" class="fa fa-home"></i>'],
    ['fa-hotel', '<i aria-hidden="true" class="fa fa-hotel"></i>'],
    ['fa-server', '<i aria-hidden="true" class="fa fa-server"></i>'],
    ['fa-hourglass', '<i aria-hidden="true" class="fa fa-hourglass"></i>'],
    ['fa-hourglass-1', '<i aria-hidden="true" class="fa fa-hourglass-1"></i>'],
    ['fa-hourglass-2', '<i aria-hidden="true" class="fa fa-hourglass-2"></i>'],
    ['fa-hourglass-3', '<i aria-hidden="true" class="fa fa-hourglass-3"></i>'],
    ['fa-hourglass-end', '<i aria-hidden="true" class="fa fa-hourglass-end"></i>'],
    ['fa-hourglass-half', '<i aria-hidden="true" class="fa fa-hourglass-half"></i>'],
    ['fa-hourglass-o', '<i aria-hidden="true" class="fa fa-hourglass-o"></i>'],
    ['fa-hourglass-start', '<i aria-hidden="true" class="fa fa-hourglass-start"></i>'],
    ['fa-i-cursor', '<i aria-hidden="true" class="fa fa-i-cursor"></i>'],
    ['fa-id-badge', '<i aria-hidden="true" class="fa fa-id-badge"></i>'],
    ['fa-id-card', '<i aria-hidden="true" class="fa fa-id-card"></i>'],
    ['fa-id-card-o', '<i aria-hidden="true" class="fa fa-id-card-o"></i>'],
    ['fa-mail-reply-all', '<i aria-hidden="true" class="fa fa-mail-reply-all"></i>'],
    ['fa-reply', '<i aria-hidden="true" class="fa fa-reply"></i>'],
    ['fa-reply-all', '<i aria-hidden="true" class="fa fa-reply-all"></i>'],
    ['fa-retweet', '<i aria-hidden="true" class="fa fa-retweet"></i>'],
    ['fa-wrench', '<i aria-hidden="true" class="fa fa-wrench"></i>'],
    ['fa-book', '<i aria-hidden="true" class="fa fa-book"></i>'],
    ['fa-database', '<i aria-hidden="true" class="fa fa-database"></i>']]

for item in ICON_LIST:
    item[1] = mark_safe(item[1])
class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['title', 'icon']
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control'}),
            'icon':forms.RadioSelect(choices=ICON_LIST,attrs={'class':'clearfix'})
        }

class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['title', 'url', 'name']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['title',]
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'})
        }
class SecondMenuModelForm(BootStrapModelForm):
    class Meta:
        model = Permission
        exclude = ['pid']

class MultiAddPermissionForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"})
    )
    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"})
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"})
    )
    menu_id = forms.ChoiceField(
        choices=[(None, '-----')],
        widget=forms.Select(attrs={'class': "form-control"}),
        required=False,

    )

    pid_id = forms.ChoiceField(
        choices=[(None, '-----')],
        widget=forms.Select(attrs={'class': "form-control"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_id'].choices += Menu.objects.values_list('id', 'title')
        self.fields['pid_id'].choices += Permission.objects.filter(pid__isnull=True).exclude(
            menu__isnull=True).values_list('id', 'title')


class MultiEditPermissionForm(forms.Form):
    id = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"})
    )
    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"})
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"})
    )
    menu_id = forms.ChoiceField(
        choices=[(None, '-----')],
        widget=forms.Select(attrs={'class': "form-control"}),
        required=False,

    )

    pid_id = forms.ChoiceField(
        choices=[(None, '-----')],
        widget=forms.Select(attrs={'class': "form-control"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_id'].choices += Menu.objects.values_list('id', 'title')
        self.fields['pid_id'].choices += Permission.objects.filter(pid__isnull=True).exclude(
            menu__isnull=True).values_list('id', 'title')
