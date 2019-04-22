from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from utils import crypt_password
import uuid
from django.utils.text import slugify
import random
import string
# Create your models here.

class IDC(models.Model):
    name = models.CharField(max_length=32,unique=True,verbose_name=u'机房',error_messages={'unique':'该机房已存在，请不要重复添加'})
    servers = models.ManyToManyField('Hosts')
    ctime = models.DateTimeField(default=datetime.now,verbose_name=u'创建时间')
    utime = models.DateTimeField(auto_now=True,verbose_name=u'更新时间')
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'idc'
        verbose_name = u'机房'
        verbose_name_plural = verbose_name
class Hosts(models.Model):
    ASSET_STATUS = (
        ('online','上线'),
        ('offline','下线')
    )
    ASSET_TYPE = (
        ('physical','物理机'),
        ('virtual','虚拟机'),
        ('instance','云主机')
    )
    hostname = models.CharField(max_length=32,verbose_name='主机名',unique={'unique':'主机名已存在'})
    server_type = models.CharField(choices=ASSET_TYPE,default='instance',max_length=10,verbose_name=u'服务器类型')
    wip = models.GenericIPAddressField(verbose_name=u'外网IP',unique=True,error_messages={'blank':'外网地址不能为空','unique':'该外网地址已存在'})
    nip = models.GenericIPAddressField(verbose_name=u'内网IP',unique=True,error_messages={'blank':'内网地址不能为空','unique':'该内网地址已存在'})
    status = models.CharField(max_length=10,choices=ASSET_STATUS,default='offline',verbose_name='状态')
    instance_id = models.CharField(max_length=64,verbose_name=u'云服务器ID',blank=True,null=True)
    sn = models.CharField(max_length=64,blank=True,null=True,verbose_name='SN编号')
    cpu_info = models.CharField(max_length=128,verbose_name='CPU',blank=True,null=True)
    os = models.CharField(max_length=64,blank=True,null=True,verbose_name='系统')
    memory = models.CharField(max_length=12,verbose_name=u'内存/G',blank=True,null=True)
    disk = models.CharField(max_length=12,verbose_name=u'硬盘/G',blank=True,null=True)
    user = models.ForeignKey('HostUsers', verbose_name=u'系统用户',blank=True,null=True)
    ctime = models.DateTimeField(default=datetime.now,verbose_name=u'创建时间')
    utime = models.DateTimeField(auto_now=True,verbose_name=u'更新时间')
    desc = models.CharField(max_length=200,verbose_name=u'描述',blank=True,null=True)
    server_id = models.CharField(max_length=12,blank=True,null=True,verbose_name=u'ServerID')
    game_id = models.CharField(max_length=12,blank=True,null=True,verbose_name=u'GameID')
    host_vars = models.TextField(blank=True, null=True, verbose_name='主机变量')
    def __str__(self):
        return self.hostname

    def gethostname(self):
        return slugify('{0} {1} {2} {3}'.format(self.nip, self.wip, self.hostname, ''.join(
            random.choice(string.ascii_letters) for _ in range(15)).lower()))

    def getrandomid(self):
        return '{0}{1}'.format(self.pk, ''.join(random.choice(string.ascii_letters) for _ in range(15)).lower())
    class Meta:
        db_table = 'hosts'
        verbose_name = u'资产'
        verbose_name_plural = verbose_name
        permissions = (
            ("can_connect_serverinfo", "可以连接主机"),
            ("can_kill_serverinfo", "可以强制用户下线"),
            ("can_monitor_serverinfo","可以查看录像"),
            ("can_view_serverinfo", "可以查看主机"),
            ("can_filemanage_serverinfo", "可以管理文件"),
        )



class  HostUsers(models.Model):
    name = models.CharField(max_length=32,unique=True,verbose_name=u'名称')
    auth_method_choices = (
        ('ssh-password','SSH/Password'),
        ('ssh-key','SSH/KEY')
    )
    auth_method = models.CharField(choices=auth_method_choices,max_length=16,verbose_name=u'认证类型',default='ssh-password')
    username = models.CharField(max_length=32,verbose_name=u'用户名')
    ssh_port = models.IntegerField(default=22,verbose_name=u'端口')
    password = models.CharField(blank=True,null=True,max_length=128,verbose_name=u'密码')
    key = models.TextField(blank=True,null=True,verbose_name='秘钥串')
    def save(self,*args,**kwargs):
        c = crypt_password.AESCipher
        self.password = c().encrypt(self.password)
        super(HostUsers,self).save(*args,**kwargs)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'remoteuser'
        verbose_name = u'主机用户信息'
        verbose_name_plural = verbose_name

class HostGroup(models.Model):
    name = models.CharField(max_length=32,verbose_name=u'主机组名',unique=True)
    host = models.ManyToManyField('Hosts')
    ctime = models.DateTimeField(default=datetime.now,verbose_name=u'创建时间')
    utime= models.DateTimeField(auto_now=True,verbose_name=u'更新时间')
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'hostgroup'
        verbose_name = u'主机组'
        verbose_name_plural = verbose_name

class UserHostPer(models.Model):
    user = models.ForeignKey('users.UserProfile',verbose_name='用户',unique=True)

    host_groups = models.ManyToManyField(HostGroup, verbose_name='授权主机组', blank=True)
    bind_hosts = models.ManyToManyField(Hosts, verbose_name='授权主机', blank=True)
    ctime = models.DateTimeField(default=datetime.now, verbose_name=u'创建时间')
    utime = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    def __str__(self):
        return self.user.username
    class Meta:
        db_table ='hostper'
        verbose_name = u'用户连接主机权限'
        verbose_name_plural = verbose_name