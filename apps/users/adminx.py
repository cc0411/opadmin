
# -*- coding: utf-8 -*-

import xadmin
from xadmin import views
from .models import Role,Menu,Permission

class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True

xadmin.site.register(views.BaseAdminView,BaseSetting)

class GlobalSettings(object):
    site_title = "运维管理系统后台"
    site_footer ="corp 2018"
# 将头部与脚部信息进行注册:
xadmin.site.register(views.CommAdminView, GlobalSettings)

class PermissionAdmin(object):
    list_display =['title','url','menu']
    search_fields =['title',]
    list_filter =['title',]

class MenuAdmin(object):
    list_display =['title',]
    search_fields =['title',]
    list_filter =['title']

#class HostPermissionAdmin(object):
#    list_display =['user','permissions','groups','createdatetime','updatedatetime']
#    search_fields =['user',]
#    list_filter =['user',]

class RoleAdmin(object):
    list_display =['title','permissions']
    search_fields =['title',]
    list_filter =['title']
xadmin.site.register(Role,RoleAdmin)
xadmin.site.register(Menu,MenuAdmin)
xadmin.site.register(Permission,PermissionAdmin)
#xadmin.site.register(HostPermission,HostPermissionAdmin)