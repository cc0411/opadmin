from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets,mixins
from .serializer import  UserInfoSerializers,RoleSerializers,MenuSerializers,PermissionSerializers
from rest_framework.permissions import IsAuthenticated
from .models import Role,Permission,Menu
User = get_user_model()
# Create your views here.



class  UserInfoViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    serializer_class = UserInfoSerializers
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated,]
    #lookup_field = "username"
    def get_object(self):
        return self.request.user

#class  HostPermissionViewSet(viewsets.ModelViewSet):
#    serializer_class =  HostPermissionSerializers
#    queryset = HostPermission.objects.all()
#    permission_classes =  [IsAuthenticated,]
#    def get_object(self):
#        return self.request.user
class  RoleViewSet(viewsets.ModelViewSet):
    serializer_class =  RoleSerializers
    queryset = Role.objects.all()
    permission_classes =  [IsAuthenticated,]
    def get_object(self):
        return self.request.user
class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializers
    queryset = Menu.objects.all()
    permission_classes = [IsAuthenticated,]

class PermissionViewSet(viewsets.ModelViewSet):
    serializer_class = PermissionSerializers
    queryset = Permission.objects.all()
    permission_classes = [IsAuthenticated,]