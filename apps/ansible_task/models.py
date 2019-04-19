from django.db import models
from django.contrib.auth import  get_user_model
from datetime import datetime
# Create your models here.

User = get_user_model()
class AnsibleOperLog(models.Model):
    user = models.ForeignKey(User,verbose_name='操作者')
    remote_ip = models.GenericIPAddressField(verbose_name='操作者IP')
    module = models.CharField(max_length=128,verbose_name='模块')
    args = models.CharField(max_length=256,verbose_name='模块参数',blank=True,null=True)
    server = models.TextField(verbose_name='服务器')
    result = models.TextField(verbose_name='执行结果')
    ctime = models.DateTimeField(verbose_name='操作时间',default=datetime.now)
    class Meta:
        db_table = 'modulelog'
        verbose_name = '模块执行记录'
        verbose_name_plural = verbose_name
    def __str__(self):
        return '%s-%s-%s' %(self.user.name,self.module,self.server)

class  Inventory(models.Model):
    groupname = models.CharField(max_length=32,unique=True,verbose_name='组名')
    hosts = models.ManyToManyField('asset.Hosts',verbose_name='主机')
    vars = models.TextField(verbose_name='变量',blank=True,null=True)
    memo = models.TextField(verbose_name='描述',blank=True,null=True)
    ctime = models.DateTimeField(verbose_name='创建时间',default=datetime.now)
    def __str__(self):
        return self.groupname
    class Meta:
        db_table = 'inventory'
        verbose_name = '动态主机表'
        verbose_name_plural = verbose_name

class PlayBooks(models.Model):
    name = models.CharField(max_length=64,verbose_name='名称')
    file = models.FileField(upload_to='playbook/%Y/%m/%d/')
    content = models.TextField(verbose_name='内容')
    user = models.ForeignKey(User,verbose_name='添加人')
    ctime = models.DateTimeField(verbose_name='添加时间',default=datetime.now)
    desc  = models.TextField(verbose_name='描述',blank=True,null=True)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'playbooks'
        verbose_name = '剧本信息'
        verbose_name_plural = verbose_name

class PlayBookLogs(models.Model):
    user = models.ForeignKey(User,verbose_name='操作者')
    remote_ip = models.GenericIPAddressField(verbose_name='操作者IP')
    name = models.CharField(max_length=64,verbose_name='剧本名称')
    result = models.TextField(verbose_name='执行结果')
    ctime = models.DateTimeField(default=datetime.now,verbose_name='执行时间')
    def __str__(self):
        return '%s-%s' %(self.user.name,self.name)
    class Meta:
        db_table ='playbooklogs'
        verbose_name = '剧本执行日志'
        verbose_name_plural = verbose_name

class AnsibleRole(models.Model):
    name = models.CharField(max_length=100, verbose_name='role名称', unique=True)
    file = models.FileField(upload_to='roles/')
    user = models.ForeignKey(User, verbose_name='添加人员')
    ctime = models.DateTimeField(default=datetime.now, verbose_name='添加日期')
    desc = models.TextField(verbose_name='描述', null=True, blank=True)

    class Meta:
        db_table = 'ansiblerole'
        verbose_name = 'AnsibleRole信息表'
        verbose_name_plural = 'AnsibleRole信息表'
