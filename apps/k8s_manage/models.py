from django.db import models

# Create your models here.
class K8sHost(models.Model):
    k8s_api = models.CharField(max_length=64, verbose_name=u"k8s连接地址",unique=True,help_text="例如 https://10.255.56.250:6443")
    k8s_api_token = models.TextField(verbose_name=u'k8s连接token',help_text="参考 apiserver token")
    k8s_ws = models.CharField(max_length=64, verbose_name=u"k8s连接地址",unique=True,help_text="例如 ws://10.255.56.250:8080")
    k8s_ws_token = models.CharField(max_length=255,verbose_name=u'k8s websoket连接token',help_text="参考 ws token")
    k8s_name = models.CharField(max_length=255,verbose_name='k8s集群名称',default='default')

    def __str__(self):
        return self.k8s_name

    class Meta:
        verbose_name = "k8s配置"
        verbose_name_plural = verbose_name


class K8sexec(K8sHost):
    class Meta:
        verbose_name = "k8s管理"
        verbose_name_plural = verbose_name
        proxy = True