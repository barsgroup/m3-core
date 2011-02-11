#coding:utf-8

from m3.contrib.kladr import models

def geo_rows_query(parent = None, filter = None):
    '''
    Возвращает QuerySet для отбора записей из подсправочника KladrGeo
    '''
    if parent == '-1':
        parent = None
    rows = models.KladrGeo.objects.filter(parent=parent)
    return rows

def geo_streets_query(parent, filter):
    '''
    Возвращает QuerySet для отбора записей подсправочника KladrStreet
    '''
    streets = models.KladrGeo.objects.get(pk=parent)
    return streets.kladrstreet_set.all()

