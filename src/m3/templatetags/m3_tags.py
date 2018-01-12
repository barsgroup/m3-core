# coding:utf-8
from django import template

from m3.actions import urls


register = template.Library()


@register.simple_tag
def action_url(shortname):
    '''
    Темплейт таг, который возвращает URL экшена
    '''
    return urls.get_url(str(shortname))
