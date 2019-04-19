# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import OperationLog,CdnLog

class OperationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationLog
        fields = '__all__'

class CdnLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CdnLog
        fields = '__all__'