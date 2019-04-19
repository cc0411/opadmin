from django.db import models
from datetime import datetime
from utils import crypt_password
# Create your models here.


class DbConfig(models.Model):
    server = models.OneToOneField('asset.Hosts',verbose_name='服务器')
    port = models.SmallIntegerField(default=3306,verbose_name='端口')
    name = models.CharField(max_length=32,verbose_name='数据库名称')
    user = models.CharField(max_length=32,verbose_name='数据库用户')
    password = models.CharField(max_length=64,verbose_name='数据库密码')
    memo = models.TextField(blank=True,null=True,verbose_name='描述')
    def save(self,*args,**kwargs):
        c = crypt_password.AESCipher
        self.password = c().encrypt(self.password)
        super(DbConfig,self).save(*args,**kwargs)
    class Meta:
        db_table = 'dbconfig'
        verbose_name ='数据库配置'
        verbose_name_plural = verbose_name
        unique_together = ('server','user','password')
    def __str__(self):
        return '%s-%s' %(self.server.nip,self.name)

class DbLogs(models.Model):
    conf = models.ForeignKey(DbConfig,verbose_name='DB配置')
    user = models.ForeignKey('users.UserProfile',verbose_name='操作用户')
    sql = models.TextField(verbose_name='执行sql')
    result = models.TextField(verbose_name='执行结果')
    ctime = models.DateTimeField(default=datetime.now,verbose_name='执行时间')
    class Meta:
        db_table ='dblogs'
        verbose_name ='DB日志'
        verbose_name_plural =verbose_name
    def __str__(self):
        return self.conf.name


