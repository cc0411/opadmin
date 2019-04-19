# -*- coding: utf-8 -*-

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role,Menu,Permission
from django.contrib.auth.models import Permission as AuthPermission
User = get_user_model()

class UserInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','name','email','mobile','image','is_superuser','roles')

#class HostPermissionSerializers(serializers.ModelSerializer):
#    permissions=AuthPermission.objects.filter(content_type__app_label__in=['asset',],codename__contains='can_')
#    class Meta:
#        model = HostPermission
#        fields = ('user','groups','permissions')

class MenuSerializers(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

class PermissionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class RoleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

