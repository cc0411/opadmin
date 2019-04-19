from django.shortcuts import render
from rest_framework import viewsets,mixins
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog,CommandLog
from .serializer import AuditLogSerializers,CommandLogSerializers
# Create your views here.


class AuditLogViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    serializer_class = AuditLogSerializers
    queryset = AuditLog.objects.all()
    permission_classes = [IsAuthenticated, ]

class CommandlogViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    serializer_class = CommandLogSerializers
    queryset = CommandLog.objects.all()
    permission_classes = [IsAuthenticated, ]
