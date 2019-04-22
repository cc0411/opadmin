"""opadmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from .settings import MEDIA_ROOT,DEBUG

from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import  DefaultRouter

from rest_framework_jwt.views import obtain_jwt_token
from asset.api import HostGroupViewSet,HostUserViewSet,HostViewSet,IDCViewSet
from users.api import UserInfoViewSet,RoleViewSet,PermissionViewSet,MenuViewSet
from webterminal.api import AuditLogViewSet,CommandlogViewSet
from workplan.api import OperationLogViewSet,CdnLogViewSet
from ansible_task.api import InventoryViewSet
from django.views.generic import TemplateView

router = DefaultRouter()
router.register(r'assets',HostViewSet,base_name='assets'),
router.register(r'idc',IDCViewSet,base_name='idc')
router.register(r'group',HostGroupViewSet,base_name='group')
router.register(r'remoteuser',HostUserViewSet,base_name='remoteuser')

router.register(r'users',UserInfoViewSet,base_name='users')
#router.register(r'hostpermission',PermissionViewSet,base_name='hostpermission')
router.register(r'menu',MenuViewSet,base_name='menu')
router.register(r'permission',PermissionViewSet,base_name='permission')
router.register(r'role',RoleViewSet,base_name='role')

router.register(r'auditlog',AuditLogViewSet,base_name='auditlog')
router.register(r'commandlog',CommandlogViewSet,base_name='commandlog')

router.register(r'operaticonlog',OperationLogViewSet,base_name='operaticonlog')
router.register(r'cdnlog',CdnLogViewSet,base_name='cdnlog')
router.register(r'inventory',InventoryViewSet,base_name='Inventory')

import xadmin
xadmin.autodiscover()

from xadmin.plugins import xversion
xversion.register_models()

from users.views import LoginView,Dashboard,LogoutView,WxLogin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^xadmin/', include(xadmin.site.urls)),  # 添加新路由
    #django默认认证
    url(r'^api-auth/', include('rest_framework.urls')),
    #rest文档页
    url(r'docs/',include_docs_urls(title="OMS")),
    #路由
    url(r'^api/', include(router.urls)),
    #jwt的认证接口,用于获取token   header加入Authorization: JWT <your_token>
    url(r'^jwt_login/$', obtain_jwt_token),
    #url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    #url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^login/$',LoginView.as_view(),name='login'),
    url(r'^wxlogin/$',WxLogin.as_view(),name='wxlogin'),
    url(r'^logout/$',LogoutView.as_view(),name='logout'),
    url(r'^index/$',Dashboard.as_view(),name='index'),
    url(r'^elfinder/', include('elfinder.urls')),
    url(r'^work/',include('workplan.urls',namespace='workplan')),
    url(r'^host/',include('asset.urls',namespace='host')),
    url(r'^user/',include('users.urls',namespace='user')),
    url(r'^webssh/',include('webterminal.urls',namespace='webssh')),
    url(r'^ueditor/',include('DjangoUeditor.urls' )),
    url(r'^wiki/',include('wiki.urls',namespace='wiki')),
    url(r'^task/',include('ansible_task.urls',namespace='ansible_task')),
    url(r'^db/',include('db_operation.urls',namespace='db')),
    url(r'^pro/',include('probuild.urls',namespace='pro')),
]
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
if DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, { 'document_root': MEDIA_ROOT, }),
    ]