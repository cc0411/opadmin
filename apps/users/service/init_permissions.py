# -*- coding:utf-8 -*-
from django.conf import settings
def initial_session(user,request):
    #登陆成功保存权限信息并去重distinct（）
    permission_list = user.roles.filter(permissions__isnull=False).values('permissions__id',
                                                                              'permissions__title',
                                                                              'permissions__url',
                                                                              'permissions__name',
                                                                              'permissions__pid_id',
                                                                              'permissions__pid__title',
                                                                              'permissions__pid__url',
                                                                              'permissions__menu_id',
                                                                              'permissions__menu__title',
                                                                             'permissions__menu__icon').distinct()
    print(permission_list)
    #存放权限信息(二级菜单)
    permission_dict ={}
    #存放菜单信息
    menu_dict = {}
    for item in permission_list:
        permission_dict[item['permissions__name']] = {
            'id': item['permissions__id'],
            'title': item['permissions__title'],
            'url': item['permissions__url'],
            'pid': item['permissions__pid_id'],
            'p_url': item['permissions__pid__url'],
            'p_title': item['permissions__pid__title'],
        }

        menu_id = item['permissions__menu_id']
        if not menu_id:
            continue

        node = {
            'id': item['permissions__id'],
            'title': item['permissions__title'],
            'url': item['permissions__url']
        }
        if menu_id in menu_dict:
            menu_dict[menu_id]['children'].append(node)
        else:
            menu_dict[menu_id] = {
                'title': item['permissions__menu__title'],
                'icon': item['permissions__menu__icon'],
                'children': [
                    node,
                ]
            }

    #print('权限列表', permission_dict)
    #print('菜单权限', menu_dict)
    # 将当前登录人的权限列表注入session中
    request.session[settings.PERMISSION_SESSION_KEY] = permission_dict
    # 将当前登录人的菜单权限字典注入session中
    request.session[settings.MENU_SESSION_KEY] = menu_dict