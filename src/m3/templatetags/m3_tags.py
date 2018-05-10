#coding:utf-8
'''
Created on 25.10.2011

@author: akvarats
'''
from __future__ import absolute_import
from django import template

from m3.actions import urls

register = template.Library()

@register.simple_tag
def action_url(shortname):
    '''
    Темплейт таг, который возвращает URL экшена
    '''
    return urls.get_url(str(shortname))
    