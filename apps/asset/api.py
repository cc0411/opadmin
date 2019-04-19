from django.shortcuts import render
from rest_framework import viewsets,mixins,generics
from .serializer import  HostGroupSerializer,HostsSerializer,IDCSerializer,HostUsersSerializer
from rest_framework.pagination import PageNumberPagination
from .models import IDC,HostUsers,HostGroup,Hosts
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 500

class HostViewSet(viewsets.ModelViewSet):
    queryset = Hosts.objects.all().order_by("-ctime")
    serializer_class = HostsSerializer
    pagination_class = CustomPagination
    filter_fields = ['status', 'server_type']
    search_fields = ('wip', 'nip', 'status', 'hostname', 'desc', 'server_type')
    ordering_fields = ('ctime', 'hostname', 'wip', 'nip')
    permission_classes = (IsAuthenticated,)
class IDCViewSet(viewsets.ModelViewSet):
    queryset = IDC.objects.all().order_by('-ctime')
    serializer_class = IDCSerializer
    permission_classes = [IsAuthenticated,]

class HostGroupViewSet(viewsets.ModelViewSet):
    queryset =  HostGroup.objects.all()
    serializer_class = HostGroupSerializer
    permission_classes = [IsAuthenticated,]

class HostUserViewSet(viewsets.ModelViewSet):
    queryset =  HostUsers.objects.all()
    serializer_class = HostUsersSerializer
    permission_classes = [IsAuthenticated,]