from .models import  Hosts,HostUsers,IDC,HostGroup

import xadmin

class AssetAdmin(object):
    list_display =['hostname','get_server_type_display','wip','nip','cpu_info','memory','disk','ctime']
    search_fields =['wip','nip']
    list_filter =['ctime','server_type']

class RemoteUserAdmin(object):
    list_display =['username','password','name',]
    search_fields =['name',]
    list_filter =['name',]
class IdcAdmin(object):
    list_display =['name','ctime']
    search_fields = ['name','ctime']
    list_filter = ['name','ctime']

class HostGroupAdmin(object):
    list_display = ['name','ctime']
    search_fields = ['name','ctime']
    list_filter = ['name','ctime']

xadmin.site.register(Hosts,AssetAdmin)
xadmin.site.register(HostUsers,RemoteUserAdmin)
xadmin.site.register(HostGroup,HostGroupAdmin)
xadmin.site.register(IDC,IdcAdmin)