# -*- coding: utf-8 -*-
from django.conf import settings
from django import template
from users.service import urls
from collections import OrderedDict
register = template.Library()

@register.inclusion_tag("_nav.html")
def get_menu_styles(request):
    """生成菜单"""

    menu_dict = request.session.get(settings.MENU_SESSION_KEY)
    key_list = sorted(menu_dict)

    ordered_dict = OrderedDict()
    for key in key_list:
        val = menu_dict[key]
        val['class'] = 'hide'
        for per in val['children']:
            if per['id'] == request.current_selected_permission:
                per['class'] = 'active'
                val['class'] = ''
        ordered_dict[key] = val
    return {
        'menu_dict': ordered_dict
    }
@register.inclusion_tag('breadcrumb.html')
def breadcrumb(request):
    """生成路径导航"""
    return {'record_list': request.breadcrumb}
        
@register.filter
def has_permission(request, name):
    """
        判断是否有权限
        :param request:
        :param name:
        :return:
        """
    if name in request.session[settings.PERMISSION_SESSION_KEY]:
        return True
@register.simple_tag
def memory_url(request, name, *args, **kwargs):
    """
    生成带有原搜索条件的URL（替代了模板中的url）
    :param request:
    :param name:
    :return:
    """
    return urls.memory_url(request, name, *args, **kwargs)