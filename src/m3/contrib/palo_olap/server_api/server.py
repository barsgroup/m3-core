#coding: utf-8
'''
Управление сервером Palo Olap
'''

import urllib
import urllib2
import hashlib
from database import PaloDataBase
from django.utils.encoding import force_unicode

class PaloOlapError(Exception):
    r"""Исключение возникающее при работе с Palo Olap"""
    pass

USE_PROXY = False

class PaloServer():
    def __init__(self, server_host = False, user = False, password = False):
        
        self.Config = PaloServerConfig()
        
        self.useProxy = USE_PROXY
        self.ProxyUrl = self.Config.getProxyUrl() ##'http://wp1.gbleo.lan:80/'
        self.ServerHost = server_host if server_host else self.Config.getPaloHost()
        self.ServerPort = self.Config.getPaloPort()
        self.ServerRoot = "http://%s:%s/" % (self.ServerHost, self.ServerPort)
        self.Client = urllib.FancyURLopener({'http': self.ProxyUrl}) if self.useProxy else urllib2
#        self.getUrlResult = urllib.FancyURLopener({'http': self.ProxyUrl}).open if self.useProxy else urllib2.urlopen
        self.User = user if user else self.Config.getPaloUser()
        md5 = hashlib.md5()
        md5.update(password)
        self.Password = md5.hexdigest() if password else self.Config.getPaloPassword()
        self.UrlEncoder = urllib.urlencode
        self.__DBList = {}
        
    def getUrlResult(self, url, **kwargs):
        if self.useProxy:
            func = urllib.FancyURLopener({'http': self.ProxyUrl}).open  
        else: 
            func = urllib2.urlopen
        try:
            res = func(url, **kwargs)
        except Exception, err:
            if err.__class__.__name__ == 'HTTPError': #сложно точно по типу
                msg = u'Error open %s (%s). \nResponse: %s' % (url, unicode(err), force_unicode(err.read()))
                raise PaloOlapError(msg)
            else:
                raise err
        return res
            
        
    
    def login(self):
        '''
        Получение идентификатора сеанса - вход на сервер
        '''
        CMD = 'server/login'
        Param = {'user': self.User,
                 'password': self.Password,
                 'sid': ', False'}
        Url = self.ServerRoot + CMD + '?' + self.UrlEncoder(Param)
        Res = self.getUrlResult(Url)
        self.Sid = Res.read().split(';')[0]
        return self.Sid

    def get_or_create_db(self, db_name):
        '''
        создание или посиск существующей базы
        '''
        self.load_db_list()
        if self.db_exists(db_name):
            # получаем базу
            db = self.get_db(db_name)
        else:
            # создаем базу
            db = self.create_db(db_name)
        return db
        

    def load_db_list(self):
        '''
        Загрузка списка баз
        '''
        CMD = 'server/databases'
        Param = {'show_normal': self.Config.ShowNormal,
                 'show_system': self.Config.ShowSystem}
        Url = self.getUrlRequest(CMD, Param)
        Res = self.getUrlResult(Url)
        for Row in Res.read().split('\n')[:-1]:
            DB = PaloDataBase(self, Row)
            self.__DBList[DB.getName()] = DB
        
    def save(self, param = {}):
        '''
        Сохранение настроек сервера (не баз и не кубов)
        '''
        CMD = 'server/save'
        Url = self.getUrlRequest(CMD, param)
        Res = self.getUrlResult(Url)
        return Res
        
    def get_db(self, db_name):
        '''
        Получение базы по имени
        '''
        return self.__DBList[db_name]
    
    def getUrlRequest(self, CMD, Param):
        '''
        Ссылка на команду управления сервером
        '''
        return self.ServerRoot + CMD + '?sid=' + self.Sid + '&' + self.UrlEncoder(Param)
        ##return '%s?sid=%s&%s' % (self.ServerRoot + CMD, self.Sid, self.UrlEncoder(Param))
        
    def create_db(self, name):
        '''
        Создание базы
        '''
        CMD = 'database/create'
        Param = {'new_name': name}
        Url = self.getUrlRequest(CMD, Param)
        Res = self.getUrlResult(Url)
        DB = PaloDataBase(self, Res.read())
        self.__DBList[name] = DB
        return DB
    
    def db_exists(self, db_name):
        '''
        Проверка наличия базы
        '''
        return db_name in self.__DBList.keys()

class PaloServerConfig(object):
    '''
    Объект настройки сервера
    '''    
    
    def __init__(self):  
        self.__PaloHost='xx.xxx.xxx.xx'  
        self.__PaloPort='7777'  
        self.__PaloUser='user' 
        self.__PaloPassword='password'
        self.__useProxy = False
        self.__ProxyUrl = 'http://host:port/'
        self.__ShowNormal = 1
        self.__ShowSystem = 0
        
    def getPaloHost(self):
        return self.__PaloHost
        
    def getPaloPort(self):        
        return self.__PaloPort
        
    def getPaloUser(self):        
        return self.__PaloUser
        
    def getPaloPassword(self):
        md5 = hashlib.md5()
        md5.update(self.__PaloPassword)
        
        return md5.hexdigest()        
    
    def getProxyUrl(self):
        return self.__ProxyUrl
    
    def useProxy(self):
        return self.__useProxy
    
    def _setShowNormal(self, Val = True):
        self.__ShowNormal = 1 if Val else 0
        
    def _getShowNormal(self, Val = True):
        return self.__ShowNormal

    def _setShowSystem(self, Val = False):
        self.__ShowSystem = 1 if Val else 0
        
    def _getShowSystem(self, Val = False):
        return self.__ShowSystem
    
    ShowNormal = property(_getShowNormal, _setShowNormal)
    ShowSystem = property(_getShowSystem, _setShowSystem)