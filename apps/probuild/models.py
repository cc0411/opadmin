from django.db import models
from  datetime import datetime
from utils import crypt_password
# Create your models here.

class RepoConfig(models.Model):
    repo_name = models.CharField(max_length=32,verbose_name='仓库名')
    repo_type = models.CharField(choices=(('git','git'),('svn','svn')),verbose_name='仓库类型',max_length=3)
    repo_user = models.CharField(verbose_name='账户名',max_length=32)
    repo_password= models.CharField(verbose_name='密码',max_length=64)
    repo_url = models.CharField(verbose_name='仓库地址',max_length=128)
    repo_model = models.CharField(verbose_name='版本类型',choices=(('brach','brach'),('tag','tag'),('trunk','trunk')),max_length=5)
    ctime = models.DateTimeField(default=datetime.now,verbose_name='创建时间')
    def save(self,*args,**kwargs):
        c = crypt_password.AESCipher
        self.repo_password = c().encrypt(self.repo_password)
        super(RepoConfig,self).save(*args,**kwargs)
    def __str__(self):
        return self.repo_name
    class Meta:
        db_table ='repoconfig'
        verbose_name ='仓库'
        verbose_name_plural = verbose_name

class ProConfig(models.Model):
    name = models.CharField(max_length=32,verbose_name='项目名称')
    env =models.CharField(choices=(('test','测试环境'),('pod','生产环境')),max_length=4,verbose_name='环境')
    repo = models.ForeignKey(RepoConfig,verbose_name='仓库')
    checkout_dir = models.CharField(max_length=128,verbose_name='代码检出目录')
    exclude = models.TextField(verbose_name='排除的文件',blank=True,null=True)
    deploy_server = models.ForeignKey('asset.Hosts',verbose_name='目标服务器')
    deploy_dir = models.CharField(max_length=128,verbose_name='目标服路径')
    deploy_release = models.CharField(max_length=128,verbose_name='目标服版本地址')
    build_num = models.SmallIntegerField(default=10,verbose_name='版本保留数')
    prev_deploy = models.TextField(blank=True, verbose_name='代码检出前操作', default='')
    post_deploy = models.TextField(blank=True, verbose_name='代码检出后操作', default='')
    prev_release = models.TextField(blank=True, verbose_name='切换版本前操作', default='')
    post_release = models.TextField(blank=True, verbose_name='切换版本后操作', default='')
    versions = models.TextField(blank=True, verbose_name='存储部署过的版本', default='')
    wx_notice = models.BooleanField(blank=True, verbose_name='是否开启微信通知', default=False)
    to_mail = models.TextField(blank=True, default='', verbose_name='收件人邮箱')
    cc_mail = models.TextField(blank=True, default='', verbose_name='抄送人邮箱')
    user = models.ForeignKey('users.UserProfile',verbose_name='负责人')
    memo = models.TextField(verbose_name='描述',blank=True,null=True)
    class Meta:
        db_table ='proconfig'
        verbose_name ='项目表'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name

class DeployLog(models.Model):
    pro = models.ForeignKey(ProConfig,verbose_name='项目')
    user = models.ForeignKey('users.UserProfile',verbose_name='执行者')
    type = models.CharField(verbose_name='操作类型',choices=(('deploy','deploy'),('rollback','rollback')),max_length=12)
    tag = models.CharField(default='master',max_length=32,verbose_name='分支或标签名')
    release_name = models.CharField(max_length=128,verbose_name='部署版本')
    release_desc = models.CharField(max_length=128,verbose_name='描述')
    result = models.TextField(verbose_name='执行日志')
    ctime = models.DateTimeField(default=datetime.now,verbose_name='执行时间')
    class Meta:
        db_table ='deploylog'
        verbose_name = '部署记录表'
        verbose_name_plural = verbose_name
