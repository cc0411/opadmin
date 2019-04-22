# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
from opadmin import celery_app
from .models import DeployLog
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task
def deploy_log(pro,user,type,tag,release_name,release_desc,result):
    try:
        DeployLog.objects.create(
            pro =pro,user=user,type=type,tag=tag,release_name=release_name,release_desc=release_desc,result=result)
    except Exception as e:
        logger.error('添加部署操作记录失败，原因：{}'.format(e))