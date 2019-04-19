# -*- coding: utf-8 -*-

from rest_framework import serializers
from .models import Hosts,HostGroup,HostUsers,IDC


class IDCSerializer(serializers.ModelSerializer):
    servers = serializers.SlugRelatedField(queryset=Hosts.objects.all(),slug_field='wip',many=True)
    class Meta:
        model = IDC
        fields = '__all__'

class HostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hosts
        fields = '__all__'

class HostGroupSerializer(serializers.ModelSerializer):
    host =serializers.SlugRelatedField(queryset=Hosts.objects.all(),slug_field='wip',many=True)
    class Meta:
        model = HostGroup
        fields = '__all__'

class HostUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostUsers
        fields = '__all__'