#coding: utf-8

from __future__ import absolute_import
from operator import attrgetter as _attrgetter
from django.db.models.fields.related import RelatedField as _RelatedField
import six
from functools import reduce


#==============================================================================
def matcher(include=None, exclude=None):
    """
    Возвращет предикат, возвращающий True для строк,
    подходящих под образцы из include и
    не подходящих под образцы из exclude
    Образцы имеют вид
    - 'xyz'  -> строка должна полностью совпасть с образцом
    - '*xyz' -> строка должна оканчиваться образцом
    - 'xyz*' -> строка должна начинаться с образца

    >>> filter(matcher(['a*', 'b*', '*s', 'cat', 'dog'], ['*ee', 'dog']),
    ...        'cat ape apple duck see bee bean knee dog'.split())
    ['cat', 'ape', 'apple', 'bean']

    >>> filter(mather(include=['*s']), ['hour', 'hours', 'day', 'days'])
    ['hours', 'days']

    >>> filter(mather(exclude=['*s']), ['hour', 'hours', 'day', 'days'])
    ['hour', 'day']
    """
    def make_checker(patterns, default=True):
        matchers = []
        for pattern in list(patterns or ()):
            if pattern.endswith('*'):
                func = (lambda p: lambda s: s.startswith(p))(pattern[:-1])
            elif pattern.startswith('*'):
                func = (lambda p: lambda s: s.endswith(p))(pattern[1:])
            else:
                func = (lambda p: lambda s: s == p)(pattern)
            matchers.append(func)
        if matchers:
            return lambda s: any(func(s) for func in matchers)
        else:
            return lambda s: default

    must_be_keeped = make_checker(include)
    must_be_droped = make_checker(exclude, default=False)
    return lambda x: must_be_keeped(x) and not must_be_droped(x)


#==============================================================================
# model to dict
#==============================================================================
def model_to_dict(obj, include=None, exclude=None):
    """
    Сериализует объект модели в словарь полностью или частично
    в зависимости от допусков и исключений

    Исключения и допуски имеют вид:
    - 'person'
    - '*_id'
    - 'user*'

    :param obj: экземпляр модели
    :type obj: object
    :param include: список допусков
    :type include: list
    :param exclude: список исключений
    :type exclude: list
    :return: словарь - результат сериализации модели
    :rtype: dict
    """
    permitted = matcher(include, exclude)
    res = {}
    for fld in obj.__class__._meta.fields:
        attr = fld.attname
        if permitted(attr):
            is_fk = isinstance(fld, _RelatedField)
            if is_fk:
                assert fld.attname.endswith('_id')
                attr = attr[:-3]
            try:
                val = _attrgetter(attr)(obj)
            except AttributeError:
                continue
            except Exception as e:
                if is_fk and isinstance(e, fld.rel.to.DoesNotExist):
                    continue
                raise
            if is_fk and val is not None:
                val = {
                    'id': getattr(val, 'id', None),
                    '__unicode__': six.text_type(val)
                }
            res[fld.attname] = val
    return res


def _setattr_deep(obj, attr, value):
    path = attr.split('.')
    path, last = path[:-1], path[-1]
    target = reduce(getattr, path, obj)
    setattr(target, last, value)
    return obj


def update_model(obj, data, include=None, exclude=None):
    """
    Заполняет поля экземпляра модели данными полностью или частично
    в зависимости от допусков и исключений

    Исключения и допуски имеют вид:
    - 'person'
    - '*_id'
    - 'user*'

    :param obj: экземпляр модели
    :type obj: object
    :param data: dict-подобный объект с данными (например, requets.REQUEST)
    :type data: dict
    :param include: список допусков
    :type include: list
    :param exclude: список исключений
    :type exclude: list
    """
    permitted = matcher(include, exclude)
    for fld in obj.__class__._meta.fields:
        attr = fld.attname
        if permitted(attr) and attr in data:
            try:
                _setattr_deep(obj, attr, data[attr])
            except AttributeError:
                pass
    return obj