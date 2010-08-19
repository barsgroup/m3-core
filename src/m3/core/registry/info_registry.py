#coding: utf-8

from datetime import datetime
from calendar import calendar

from django.db import models
from django.db.models.query_utils import Q

PERIOD_INFTY = 0 # в регистре нет периодичности и нет динамически хранящихся
PERIOD_SECOND = 1 # до секунд
PERIOD_MINUTE = 2
PERIOD_HOUR = 3
PERIOD_DAY = 4
PERIOD_MONTH = 5
PERIOD_QUARTER = 6
PERIOD_YEAR = 7

def normdate(period, date, begin = True):
    '''
    Метод нормализует дату в зависимости от периода
    @ begin = True - даты выравниваются на начало, иначе на конец
    '''
    if not date:
        return None        
    if period == PERIOD_SECOND:
        return datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)
    if period == PERIOD_MINUTE:
        return datetime(date.year, date.month, date.day, date.hour, date.minute, 0 if begin else 59)
    if period == PERIOD_HOUR:
        return datetime(date.year, date.month, date.day, date.hour, 0 if begin else 59, 0 if begin else 59)
    if period == PERIOD_DAY:
        return datetime(date.year, date.month, date.day, 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
    if period == PERIOD_MONTH:
        return datetime(date.year, date.month, 1 if begin else calendar.monthrange(date.year, date.month)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
    if period == PERIOD_QUARTER:
        if date.month < 4:
            return datetime(date.year, 1 if begin else 3, 1 if begin else calendar.monthrange(date.year, 1 if begin else 3)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
        if date.month < 7:
            return datetime(date.year, 4 if begin else 6, 1 if begin else calendar.monthrange(date.year, 4 if begin else 6)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
        if date.month < 10:
            return datetime(date.year, 7 if begin else 9, 1 if begin else calendar.monthrange(date.year, 7 if begin else 9)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
        return datetime(date.year, 10 if begin else 12, 1 if begin else calendar.monthrange(date.year, 10 if begin else 12)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
    if period == PERIOD_YEAR:
        return datetime(date.year, 1 if begin else 12, 1 if begin else calendar.monthrange(date.year, 1 if begin else 12)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
    return date


class OverlapError(Exception):
    r"""Исключение возникающее при наложении интервалов друг на друга."""
    pass


class BaseInfoModel(models.Model):

    info_date_prev  = models.DateTimeField(db_index = True, default = datetime.min)
    info_date_next = models.DateTimeField(db_index = True, default = datetime.max)
    info_date = models.DateTimeField(db_index = True, blank = True)
    
    dimentions = [] # перечень реквизитов-измерений
    period = PERIOD_DAY # тип периодичности

    # сформируем запрос по ключу
    @classmethod
    def query_dimentions(cls, data):
        '''
        запрос по ключевым полям
        @data - объект, который содержит данные для сохранения в регистр.
                Это может быть либо 1) объект модели хранения данных регистра,
                либо 2) словарь, ключами которого являются имена полей из модели хранения,
                либо 3) объект любого класса, у которого есть атрибуты с именами
        '''
        # добавим в запрос фильтр по ключевым полям, со значениями = текущему объекту, переданным данным
        query = cls.objects
        for dim_field in cls.dimentions:
            dim_val = None
            dim_attr = dim_field
            if isinstance(dim_field, models.Field):
                dim_attr = dim_field.name
            if isinstance(data, BaseInfoModel):
                dim_val = getattr(data, dim_attr, None)
            elif isinstance(data, dict):
                if data.has_key(dim_attr):
                    dim_val = data[dim_attr]
            elif hasattr(data, dim_attr):
                dim_val = getattr(data, dim_attr, None)
            if dim_val:
                query = query.filter(**{dim_attr: dim_val})
        return query
    
    # сформируем запрос данных на дату
    @classmethod
    def query_on_date(cls, data, date = datetime.now(), next = False):
        '''
        запрос записей на дату
        @data - объект или словарь с ключевыми данными
        @date - дата актуальности, по умолчанию текущая
        @next = False - значит будут найдены записи, уже действущие на дату, иначе ближайшиие записи которые будут действовать
        '''
        query = cls.query_dimentions(data)
        if cls.period != PERIOD_INFTY:
            q_date = normdate(cls.period,date)
            if next:
                query = query.filter(info_date_prev__lte = q_date, info_date__gte = q_date)
            else:
                query = query.filter(info_date__lte = q_date, info_date_next__gte = q_date)
        return query
    
    # прямая запись объекта, чтобы можно было записывать без доп. обработки
    def _save(self, *args, **kwargs):
        super(BaseInfoModel, self).save(*args, **kwargs)

    # переопределим запись объекта, чтобы изменять соседние записи
    def save(self, *args, **kwargs):
        # если не указана дата записи, то
        if self.period != PERIOD_INFTY and not self.info_date:
            raise Exception('Attribute info_date is not set!')
        # нормализуем переданные дату и время 
        self.info_date = normdate(self.period,self.info_date)
        
        # проверим на уникальность записи
        if self.period != PERIOD_INFTY:
            q = self.__class__.query_dimentions(self).filter(info_date = self.info_date)
            if self.pk:
                q = q.exclude(pk = self.pk)
            if q.count() > 0:
                raise OverlapError()
        # если объект уже хранится, то найдем записи для изменения
        if self.pk:
            q = self.__class__.query_dimentions(self).filter(info_date = self.info_date_prev)
            old_prev_rec = q.get() if len(q) == 1 else None
            q = self.__class__.query_dimentions(self).filter(info_date = self.info_date_next)
            old_next_rec = q.get() if len(q) == 1 else None
        else:
            old_prev_rec = None
            old_next_rec = None
        # вычислим ближайщую запись, которая начинается "левее" текущей
        q = self.__class__.query_dimentions(self).filter(info_date__lt = self.info_date, info_date_next__gte = self.info_date).exclude(pk = self.pk)
        new_prev_rec = q.get() if len(q) == 1 else None
        # вычислим ближайшую запись, которая начинается "правее" текущей
        q = self.__class__.query_dimentions(self).filter(info_date__gt = self.info_date, info_date_prev__lte = self.info_date).exclude(pk = self.pk)
        new_next_rec = q.get() if len(q) == 1 else None
        # изменим даты исходя из соседей
        if new_prev_rec:
            self.info_date_prev = new_prev_rec.info_date
        else:
            self.info_date_prev = normdate(self.period, datetime.min)
        if new_next_rec:
            self.info_date_next = new_next_rec.info_date
        else:
            self.info_date_next = normdate(self.period, datetime.max)
        # сохраним запись
        self._save(*args, **kwargs)
        # изменим найденные ранее записи
        #TODO: тут можно оптимизировать сохранение, чтобы небыло каскада сохранений
        if old_prev_rec:
            if old_prev_rec != new_prev_rec:
                old_prev_rec.save()
        if old_next_rec:
            if old_next_rec != new_next_rec:
                old_next_rec.save()
        if new_prev_rec:
            if new_prev_rec.info_date_next != self.info_date:
                new_prev_rec.info_date_next = self.info_date
                new_prev_rec._save()
        if new_next_rec:
            if new_next_rec.info_date_prev != self.info_date:
                new_next_rec.info_date_prev = self.info_date
                new_next_rec._save()

    # прямое удаление, без обработки
    def _delete(self, *args, **kwargs):
        super(BaseInfoModel, self).delete(*args, **kwargs)

    # переопределим удаление объекта, чтобы изменять соседние записи
    def delete(self, *args, **kwargs):
        # если объект уже хранится, то найдем записи для изменения
        if self.pk:
            q = self.__class__.query_dimentions(self).filter(info_date = self.info_date_prev)
            old_prev_rec = q.get() if len(q) == 1 else None
            q = self.__class__.query_dimentions(self).filter(info_date = self.info_date_next)
            old_next_rec = q.get() if len(q) == 1 else None
        else:
            old_prev_rec = None
            old_next_rec = None
        # удалим запись
        self._delete(*args, **kwargs)
        # изменим найденные ранее записи
        #TODO: тут можно оптимизировать сохранение, чтобы небыло каскада сохранений
        if old_prev_rec:
            old_prev_rec.save()
        if old_next_rec:
            old_next_rec.save()
    
    class Meta:
        abstract = True

class BaseIntervalInfoModel(models.Model):

    info_date_prev  = models.DateTimeField(db_index = True, default = datetime.min)
    info_date_next = models.DateTimeField(db_index = True, default = datetime.max)
    info_date_begin = models.DateTimeField(db_index = True, blank = True)
    info_date_end = models.DateTimeField(db_index = True, blank = True)
    
    dimentions = [] # перечень реквизитов-измерений
    period = PERIOD_DAY # тип периодичности

    # сформируем запрос по ключу
    @classmethod
    def query_dimentions(cls, data):
        '''
        запрос по ключевым полям
        @data - объект, который содержит данные для сохранения в регистр.
                Это может быть либо 1) объект модели хранения данных регистра,
                либо 2) словарь, ключами которого являются имена полей из модели хранения,
                либо 3) объект любого класса, у которого есть атрибуты с именами
        '''
        # добавим в запрос фильтр по ключевым полям, со значениями = текущему объекту, переданным данным
        query = cls.objects
        for dim_field in cls.dimentions:
            dim_val = None
            dim_attr = dim_field
            if isinstance(dim_field, models.Field):
                dim_attr = dim_field.name
            if isinstance(data, BaseInfoModel):
                dim_val = getattr(data, dim_attr, None)
            elif isinstance(data, dict):
                if data.has_key(dim_attr):
                    dim_val = data[dim_attr]
            elif hasattr(data, dim_attr):
                dim_val = getattr(data, dim_attr, None)
            if dim_val:
                query = query.filter(**{dim_attr: dim_val})
        return query
    
    # сформируем запрос на интервал дат
    @classmethod 
    def query_interval(cls, data, date_begin = datetime.min, date_end = datetime.max, include_begin = True, include_end = True):
        '''
        Выборка записей, попадающий в указанный интервал дат.
        @data - объект или словарь с ключевыми данными
        @date_begin - начало интервала
        @date_end - конец интервала
        @include_begin = True - запись учитывается если начало интервала попадает в интервал записи, иначе не учитывается
        @include_end = True - запись учитывается если конец интервала попадает в интервал записи, иначе не учитывается
        '''
        query = cls.query_dimentions(data)
        if cls.period != PERIOD_INFTY:
            date_begin = normdate(cls.period, date_begin, True)
            date_end = normdate(cls.period, date_end, False)
            filter = Q(info_date_begin__gte = date_begin) & Q(info_date_end__lte = date_end) # попадание в интервал полностью
            if include_begin:
                filter = filter | (Q(info_date_begin__lte = date_begin) & Q(info_date_end__gt = date_begin)) # попадание начала интервала в границы записи
                if include_end:
                    filter = filter | (Q(info_date_begin__lt = date_end) & Q(info_date_end__gte = date_end)) # попадание конца интервала в границы записи
        query = query.filter(filter)
        return query
    
    # сформируем запрос данных на дату
    @classmethod
    def query_on_date(cls, data, date = datetime.now(), active = True, next = False):
        '''
        запрос записей на дату
        @data - объект или словарь с ключевыми данными
        @date - дата актуальности, по-умолчанию текущая
        @active = True - значит будут найдены записи, действующие на указанную дату
        @next = False - значит будут найдены записи, действовавшие до даты, иначе ближайшиие записи которые будут действовать
        '''
        query = cls.query_dimentions(data)
        if cls.period != PERIOD_INFTY:
            q_date_begin = normdate(cls.period, date, True)
            q_date_end = normdate(cls.period, date, False)
            if next:
                filter = Q(info_date_prev__lte = q_date_begin, info_date_begin__gt = q_date_end) # дата попадает в интервал перед записью
            else:
                filter = Q(info_date_next__gt = q_date_end, info_date_end__lte = q_date_begin) # дата попадает в интервал после записи
            if active:
                filter = filter | Q(info_date_begin__lte = q_date_begin, info_date_end__gte = q_date_end) # дата попадает в интервал записи
            query = query.filter(filter)
        return query
    
    # прямая запись объекта, чтобы можно было записывать без доп. обработки
    def _save(self, *args, **kwargs):
        super(BaseIntervalInfoModel, self).save(*args, **kwargs)

    # переопределим запись объекта, чтобы изменять соседние записи
    def save(self, *args, **kwargs):
        # если не указана дата записи, то
        if self.period != PERIOD_INFTY and (not self.info_date_begin or not self.info_date_end):
            raise Exception('Attribute info_date is not set!')
        # нормализуем переданные дату и время 
        self.info_date_begin = normdate(self.period,self.info_date_begin, True)
        self.info_date_end = normdate(self.period,self.info_date_end, False)
        
        if self.period != PERIOD_INFTY and (self.info_date_begin > self.info_date_end):
            raise Exception('Interval is invalid!')
        
        # проверим на уникальность записи
        if self.period != PERIOD_INFTY:
            q = self.__class__.query_interval(self, self.info_date_begin, self.info_date_end)
            if self.pk:
                q = q.exclude(pk = self.pk)
            if q.count() > 0:
                raise OverlapError()
        
        # если объект уже хранится, то найдем записи для изменения
        old_prev_rec = None
        old_next_rec = None
        if self.pk:
            q = self.__class__.query_dimentions(self).filter(info_date_end = self.info_date_prev)
            old_prev_rec = q.get() if len(q) == 1 else None
            q = self.__class__.query_dimentions(self).filter(info_date_begin = self.info_date_next)
            old_next_rec = q.get() if len(q) == 1 else None

        # вычислим ближайщую запись, которая заканчивается "левее" текущей
        q = self.__class__.query_dimentions(self).filter(info_date_end__lte = self.info_date_begin, info_date_next__gte = self.info_date_begin)
        new_prev_rec = q.get() if len(q) == 1 else None
        # вычислим ближайшую запись, которая начинается "правее" текущей
        q = self.__class__.query_dimentions(self).filter(info_date_begin__gte = self.info_date_end, info_date_prev__lte = self.info_date_end)
        new_next_rec = q.get() if len(q) == 1 else None
        # изменим даты исходя из соседей
        if new_prev_rec:
            self.info_date_prev = new_prev_rec.info_date_end
        else:
            self.info_date_prev = normdate(self.period, datetime.min, False)
        if new_next_rec:
            self.info_date_next = new_next_rec.info_date_begin
        else:
            self.info_date_next = normdate(self.period, datetime.max, True)
        # сохраним запись
        self._save(*args, **kwargs)
        # изменим найденные ранее записи
        #TODO: тут можно оптимизировать сохранение, чтобы небыло каскада сохранений
        if old_prev_rec:
            if old_prev_rec != new_prev_rec:
                old_prev_rec.save()
        if old_next_rec:
            if old_next_rec != new_next_rec:
                old_next_rec.save()
        if new_prev_rec:
            if new_prev_rec.info_date_next != self.info_date_begin:
                new_prev_rec.info_date_next = self.info_date_begin
                new_prev_rec._save()
        if new_next_rec:
            if new_next_rec.info_date_prev != self.info_date_end:
                new_next_rec.info_date_prev = self.info_date_end
                new_next_rec._save()

    # прямое удаление, без обработки
    def _delete(self, *args, **kwargs):
        super(BaseIntervalInfoModel, self).delete(*args, **kwargs)

    # переопределим удаление объекта, чтобы изменять соседние записи
    def delete(self, *args, **kwargs):
        # если объект уже хранится, то найдем записи для изменения
        if self.pk:
            q = self.__class__.query_dimentions(self).filter(info_date_end = self.info_date_prev)
            old_prev_rec = q.get() if len(q) == 1 else None
            q = self.__class__.query_dimentions(self).filter(info_date_begin = self.info_date_next)
            old_next_rec = q.get() if len(q) == 1 else None
        else:
            old_prev_rec = None
            old_next_rec = None
        # удалим запись
        self._delete(*args, **kwargs)
        # изменим найденные ранее записи
        #TODO: тут можно оптимизировать сохранение, чтобы небыло каскада сохранений
        if old_prev_rec:
            old_prev_rec.save()
        if old_next_rec:
            old_next_rec.save()
    
    class Meta:
        abstract = True
