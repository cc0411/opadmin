# -*- coding:utf-8 -*-
from rest_framework import viewsets, permissions
from .serializers import InventorySerializer
from .models import Inventory
class InventoryViewSet(viewsets.ModelViewSet):

    queryset = Inventory.objects.all().order_by('id')
    serializer_class = InventorySerializer
    permission_classes = (permissions.IsAuthenticated,)