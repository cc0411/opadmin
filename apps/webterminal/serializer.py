# -*- coding: utf-8 -*-

from rest_framework import serializers
from .models import AuditLog,CommandLog

class AuditLogSerializers(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class CommandLogSerializers(serializers.ModelSerializer):
    class Meta:
        model = CommandLog
        fields = "__all__"
