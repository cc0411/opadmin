# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from opadmin import celery_app
from ansible_task.models import AnsibleOperLog, PlayBookLogs
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task
def module_record(ans_user, ans_remote_ip, ans_module, ans_args, ans_server, ans_result):
    try:
        AnsibleOperLog.objects.create(
            user=ans_user,
            remote_ip=ans_remote_ip,
            module=ans_module,
            args=ans_args,
            server=ans_server,
            result=ans_result,
        )
    except Exception as e:
        print(e)


@celery_app.task
def playbook_record(playbook_user, playbook_remote_ip, playbook_name, playbook_result):
    try:
        PlayBookLogs.objects.create(
            user=playbook_user,
            remote_ip=playbook_remote_ip,
            name=playbook_name,
            result=playbook_result,
        )
    except Exception as e:
        print(e)

@shared_task
def add(x, y):
    return x + y