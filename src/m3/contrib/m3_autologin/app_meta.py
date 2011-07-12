#coding:utf-8
'''
Created on 08.07.2011

@author: akvarats
'''

from django.conf import urls

from views import autologin_view

def register_urlpatterns():
    '''
    Регистрация конфигурации урлов для приложения m3.contrib.users
    '''
    return urls.defaults.patterns('',
        (r'^auto-login/(?P<login_option>.*)$', autologin_view),
    )