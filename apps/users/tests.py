from .models import  UserProfile


user = UserProfile.objects.get(username='zhangsan')
user.roles.add(1)


