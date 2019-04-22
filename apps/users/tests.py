from .models import  UserProfile


user = UserProfile.objects.get(username='zhangsan')
user.roles.update(role__id=2)


