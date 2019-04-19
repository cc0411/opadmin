from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from DjangoUeditor.models import UEditorField
User = get_user_model()
# Create your models here.

class Documents(models.Model):
    title =models.CharField(max_length=128,verbose_name=u'文档标题',unique=True)
    content = UEditorField(width=600, height=300, toolbars="full", imagePath="wiki/images/", filePath="wiki/files/",upload_settings={"imageMaxSize":1204000},settings={},verbose_name='内容')
    author = models.CharField(max_length=32,verbose_name='作者')
    ctime = models.DateTimeField(default=datetime.now,verbose_name='发表时间')
    utime = models.DateTimeField(auto_now=True,verbose_name='修改时间')
    def __str__(self):
        return self.title
    class Meta:
        db_table ='wiki'
        verbose_name = 'WiKi文档'
        verbose_name_plural = verbose_name

