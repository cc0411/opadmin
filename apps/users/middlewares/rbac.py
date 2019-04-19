# -*- coding: utf-8 -*-
import re
from django.conf import settings
from django.shortcuts import HttpResponse,redirect
from django.utils.deprecation import MiddlewareMixin


class RbacMiddleware(MiddlewareMixin):
    """
        用户权限信息校验
        """

    def process_request(self, request):
        """
        当用户请求刚进入时候出发执行
        :param request:
        :return:
        """

        """
        1. 获取当前用户请求的URL
        2. 获取当前用户在session中保存的权限列表 ['/customer/list/','/customer/list/(?P<cid>\\d+)/']
        3. 权限信息匹配
        """
        current_url = request.path_info
        for valid_url in settings.VALID_URL_LIST:
            if re.match(valid_url, current_url):
                # 白名单中的URL无需权限验证即可访问
                return None

        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        if not permission_dict:
            return redirect('login')
            #return HttpResponse('未获取到用户权限信息，请登录！')

        flag = False

        url_record = [
            {'title': '首页', 'url': '#'}
        ]

        # 此处代码进行判断
        for url in settings.NO_PERMISSION_LIST:
            if re.match(url, request.path_info):
                # 需要登录，但无需权限校验
                request.current_selected_permission = 0
                request.breadcrumb = url_record

                return None

        flag = False

        for item in permission_dict.values():
            reg = "^%s$" % item['url']
            if re.match(reg, current_url):
                flag = True
                request.current_selected_permission = item['pid'] or item['id']
                if not item['pid']:
                    url_record.extend([{'title': item['title'], 'url': item['url'], 'class': 'active'}])
                else:
                    url_record.extend([
                        {'title': item['p_title'], 'url': item['p_url']},
                        {'title': item['title'], 'url': item['url'], 'class': 'active'},
                    ])
                request.breadcrumb = url_record
                break

        if not flag:
            return HttpResponse('无权访问')