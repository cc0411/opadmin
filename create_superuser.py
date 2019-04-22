# -*- coding:utf-8 -*-
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "opadmin.settings")
import django
django.setup()
from django.contrib.auth import get_user_model
from users.models import Role,Menu
User = get_user_model()

username = 'admin'
password ='abc1234,'
email ='admin@jcwit.com'

Role.objects.create(title='管理员')
Role.objects.create(title='普通用户')
User.objects.create_superuser(username=username, email=email, password=password,name='张三',mobile='13111111111')
User.objects.get(username='admin').roles.remove(2)
User.objects.get(username='admin').roles.add(1)
Menu.objects.create(title='权限管理',icon='fa-hourglass-3')
Menu.objects.create(title='用户管理',icon='fa-users')

