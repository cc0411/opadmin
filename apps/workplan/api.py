from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets,mixins
from rest_framework.permissions import IsAuthenticated
from .models import OperationLog,CdnLog
from .serializer import OperationLogSerializer,CdnLogSerializer



class OperationLogViewSet(viewsets.ModelViewSet):
    serializer_class = OperationLogSerializer
    queryset = OperationLog.objects.all()
    permission_classes = [IsAuthenticated, ]

class CdnLogViewSet(viewsets.ModelViewSet):
    serializer_class = CdnLogSerializer
    queryset = CdnLog.objects.all()
    permission_classes = [IsAuthenticated, ]