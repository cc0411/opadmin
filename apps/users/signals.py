# -*- coding:utf-8 -*-

from  django.db.models.signals import  post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
User = get_user_model()


@receiver(post_save,sender=User)
def add_roles(sender,instance,created, update_fields,**kwargs):
    if created:
        user = User.objects.get(id =instance.id)
        user.roles.add(2)
