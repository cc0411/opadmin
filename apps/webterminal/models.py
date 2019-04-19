from django.db import models
from asset.models import Hosts,HostGroup
from django.contrib.auth import  get_user_model
import  uuid
User = get_user_model()
# Create your models here.
class AuditLog(models.Model):
    server = models.ForeignKey(Hosts,verbose_name='服务器')
    channel = models.CharField(max_length=100,verbose_name='channel',blank=False,unique=True,editable=False)
    log = models.UUIDField(max_length=100,default=uuid.uuid4,verbose_name='日志名',blank=False,unique=True,editable=False)
    start_time = models.DateTimeField(auto_now_add=True,verbose_name='开始时间')
    end_time = models.DateTimeField(auto_created=True,auto_now=True,verbose_name='结束时间')
    is_finished = models.BooleanField(default=False,verbose_name='是否完成')
    user = models.ForeignKey(User,verbose_name='执行人')
    width = models.PositiveIntegerField(default=90,verbose_name='宽度')
    height = models.PositiveIntegerField(default=40,verbose_name='高度')
    def __str__(self):
        return self.server
    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = verbose_name
        db_table ='auditlog'
        permissions = (
            ("can_delete_log", "可以删除审计日志"),
            ("can_view_log", "可以查看审计日志"),
            ("can_play_log", "可以播放审计日志"),
        )
        ordering = [
            ('-start_time')
        ]
class CommandLog(models.Model):
    log = models.ForeignKey(AuditLog, verbose_name='审计日志')
    datetime = models.DateTimeField(
        auto_now=True, verbose_name='执行时间')
    command = models.CharField(max_length=255, verbose_name='执行的命令')

    class Meta:
        verbose_name = u'命令'
        verbose_name_plural =verbose_name
        db_table = 'command'
        permissions = (
            ("can_view_command_log", "可以查看历史执行命令"),
        )
        ordering = [
            ('-datetime')
        ]
    def __str__(self):
        return self.log

