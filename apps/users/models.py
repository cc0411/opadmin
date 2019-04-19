from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Permission as AuthPermission
from django.contrib.contenttypes.models import ContentType
from asset.models import HostGroup
# Create your models here.

class UserProfile(AbstractUser):
    mobile = models.CharField(max_length=11,verbose_name=u'手机号',blank=True,null=True)
    image = models.ImageField(max_length=100,verbose_name=u'头像',upload_to='image/%Y/%m',default='image/default.png')
    name = models.CharField(max_length=32,verbose_name=u'姓名',default='')
    roles = models.ManyToManyField('Role',verbose_name=u'拥有的角色')
    def __str__(self):
        return self.username
    class Meta:
        db_table ='userprofile'
        verbose_name = u'用户'
        verbose_name_plural = verbose_name

class HostPermission(models.Model):
    '''主机管理权限'''
    user = models.OneToOneField(UserProfile, verbose_name='用户', related_name='permissionuser')
    permissions = models.ManyToManyField(
        AuthPermission, verbose_name='权限', related_name='permission')
    groups = models.ManyToManyField(
        HostGroup, verbose_name='主机组')
    createdatetime = models.DateTimeField(
        auto_now_add=True, verbose_name='创建时间')
    updatedatetime = models.DateTimeField(
        auto_created=True, auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.user.username
    class Meta:
        verbose_name  = "权限"
        verbose_name_plural = verbose_name

class  Permission(models.Model):
    '''权限表'''
    title = models.CharField(max_length=32,verbose_name=u'菜单名')
    url = models.CharField(max_length=256,verbose_name='菜单url')
    name = models.CharField(verbose_name='URL别名', max_length=64, unique=True)
    pid = models.ForeignKey(verbose_name='关联的权限', to='Permission', related_name='parents', null=True, blank=True,
                            help_text="对于无法作为菜单的URL，可以为其选择一个可以作为菜单的权限，那么访问时，则默认选中此权限")
    menu = models.ForeignKey('Menu',verbose_name=u'所属菜单', null=True, blank=True, help_text='null表示非菜单;非null表示是二级菜单')
    def __str__(self):
        return self.title
    class Meta:
        db_table ='rbac_permission'
        verbose_name = '菜单'
        verbose_name_plural = verbose_name

class Menu(models.Model):
    title = models.CharField(max_length=32,verbose_name=u'菜单')
    icon =models.CharField(max_length=32,verbose_name=u'图标',blank=True,null=True)
    def __str__(self):
        return self.title
    class Meta:
        db_table ='rbac_menu'
        verbose_name_plural ='菜单组'
        verbose_name =verbose_name_plural

class Role(models.Model):
    '''角色表'''
    title=models.CharField(max_length=32,verbose_name=u'角色名')
    permissions=models.ManyToManyField(to="Permission",verbose_name=u'拥有的所有权限', blank=True)

    def __str__(self):
        return self.title
    class Meta:
        db_table ='rbac_role'
        verbose_name = '用户角色'
        verbose_name_plural = verbose_name

class WxConfig(models.Model):
    '''
    企业微信扫码登录相关配置
    '''
    agentid = models.CharField(max_length=50,verbose_name='授权方网页应用ID')
    redirect_uri = models.CharField(max_length=255,verbose_name='重定向地址')
    state = models.CharField(max_length=255,verbose_name='状态')
    # 企业微信corpid和corpsecret
    corpid = models.CharField(max_length=128,verbose_name='CorpID')
    corp_secret = models.CharField(max_length=128,verbose_name='Secret')
    class Meta:
        db_table = 'wxconfig'
        verbose_name ='企业微信配置'
        verbose_name_plural = verbose_name