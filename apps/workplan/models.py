from django.db import models
from django.contrib.auth import  get_user_model
from datetime import datetime
# Create your models here.

User = get_user_model()

class OperationLog(models.Model):
    user = models.CharField(max_length=32,verbose_name='操作人')
    gname = models.CharField(max_length=32,verbose_name='游戏名')
    version_online = models.CharField(max_length=64,verbose_name=u'线上版本号')
    version_updated = models.CharField(max_length=64,verbose_name=u'更新版本号')
    game_package = models.CharField(max_length=64,verbose_name=u'游戏包名',default='')
    game_type_choices = ((0,"线上"),(1,"测试服"))
    game_type = models.SmallIntegerField(default=1,verbose_name=u'是否线上服',choices=game_type_choices)
    desc = models.TextField(verbose_name='描述',blank=True,null=True)
    is_new_choices = ((0, "当前版本"), (1, "跨版本"))
    is_new = models.BooleanField(default=0,verbose_name=u'是否跨版本',choices=is_new_choices)
    ctime = models.DateTimeField(default=datetime.now)
    def __str__(self):
        return '%s-%s' %(self.user,self.gname)
    class Meta:
        verbose_name = '游戏运维工作内容'
        verbose_name_plural = verbose_name


class CdnLog(models.Model):
    gname = models.CharField(verbose_name=u'游戏名',max_length=32)
    version = models.CharField(max_length=32,verbose_name='资源版本')
    is_full = models.BooleanField(default=True,verbose_name=u'是否增量')
    user = models.CharField(max_length=32,verbose_name=u'操作人')
    cdn_type_choices = ((0,'国内'),(1,'海外'))
    is_flush = models.BooleanField(default=False,verbose_name=u'是否需要刷新')
    cdn_type = models.SmallIntegerField(verbose_name='CDN类型',choices=cdn_type_choices,default=0)
    ctime = models.DateTimeField(default=datetime.now,verbose_name='执行时间')
    def __str__(self):
        return '%s-%s' %(self.user,self.gname)
    class Meta:
        verbose_name = 'CDN执行日志'
        verbose_name_plural = verbose_name
