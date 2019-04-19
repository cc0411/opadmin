# -*- coding: utf-8 -*-

from  django import forms
from users.models import UserProfile,Role
from django.utils.encoding import force_text
# 登录表单验证
class LoginForm(forms.Form):
    # 用户名密码不能为空
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=8)

# 用于文件上传，修改头像
class UploadImageForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['image']
class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
            return force_text(obj.name)

class  RegisterForm(forms.Form):
    def __init__(self,*args,**kwargs):
        self.instance = False
        if 'instance' in kwargs.keys():
            kwargs.pop('instance')
            self.instance = True
        super(RegisterForm, self).__init__(*args,**kwargs)
    username = forms.CharField(required=True,label='用户名',error_messages={'required':'请输入用户名'},max_length=32,widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(required=True,label='密码',error_messages={'required':'请输入密码'},min_length=8,widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(required=True,label='确认密码',error_messages={'required':'请输入确认密码'},min_length=8,widget=forms.PasswordInput(attrs={'class':'form-control'}))
    email = forms.EmailField(required=True,label='邮箱',error_messages={'required':'请输入邮箱'},widget=forms.EmailInput(attrs={'class':'form-control'}))
    name = forms.CharField(required=True,label='姓名',error_messages={'required':'请输入姓名'},widget=forms.TextInput(attrs={'class':'form-control'}))
    mobile = forms.CharField(required=True,label='手机',error_messages={'required':'手机号不能为空'},widget=forms.TextInput(attrs={'class':'form-control'}))
    roles = forms.ModelMultipleChoiceField(required=True,label='角色',queryset=Role.objects.all(),widget=forms.CheckboxSelectMultiple())

    def clean(self):
        if not self.is_valid():
           raise forms.ValidationError({'username':'请确保所有字段不为空'})
        elif self.cleaned_data['password'] !=self.cleaned_data['password2']:
            raise  forms.ValidationError({'password2':"密码输入不一致，请确认"})
        elif self.cleaned_data['username']:
            if not self.instance:
                if UserProfile.objects.filter(username =self.cleaned_data['username']):
                    raise forms.ValidationError({'username':'用户已存在'})
        elif self.cleaned_data['email']:
            if not self.instance:
                if UserProfile.objects.filter(email=self.cleaned_data['email']):
                    raise  forms.ValidationError({'email':'邮箱地址已存在'})
        cleaned_data = super(RegisterForm,self).clean()
        return cleaned_data




#class HostPermissionForm(forms.ModelForm):
#    permissions = CustomModelMultipleChoiceField(queryset=AuthPermission.objects.
#                                                 filter(content_type__app_label__in=['asset',], codename__contains='can_'),
#                                                 widget=forms.CheckboxSelectMultiple())
#    class Meta:
#        model = HostPermission
#        fields = ['user', 'permissions', 'groups']





