# coding:utf-8
"""Платформа разработки приложений ERP типа на python и django."""

from __future__ import absolute_import
import copy
import datetime
import decimal
import json
import sys

from django.conf import settings
from django.contrib import auth
from django.db import models as dj_models
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.utils import datetime_safe
from django.views.debug import ExceptionReporter
from m3_django_compat import ModelOptions

from .actions import ApplicationLogicException
from .actions.urls import get_app_urlpatterns
from .actions import OperationResult


def date2str(date, template=None):
    """
    datetime.strftime глючит с годом < 1900
    типа обходной маневр (взято из django)
    WARNING from django:
    # This library does not support strftime's \"%s\" or \"%y\" format strings.
    # Allowed if there's an even number of \"%\"s because they are escaped.
    """
    return datetime_safe.new_datetime(date).strftime(
        template or settings.DATE_FORMAT or '%d.%m.%Y')


class AutoLogout(object):
    '''
    Отслеживает активность пользователей в системе.
    Если с последнего действия пользователя прошло времени
    больше чем INACTIVE_SESSION_LIFETIME,
    то он выводит пользователя из системы
    '''

    session_key = 'app_last_user_activity_time'

    def process_request(self, request):
        # Если проверка отключена
        if settings.INACTIVE_SESSION_LIFETIME == 0:
            return

        # У аутентифицированного пользователя проверяем таймаут,
        # а ананимусов сразу посылаем
        if request.user.is_authenticated():
            last_time = request.session.get(self.session_key, None)
            if last_time is not None:
                delta = datetime.datetime.now() - last_time
                if delta.seconds / 60 > settings.INACTIVE_SESSION_LIFETIME:
                    # После логаута сессия уже другая
                    # и присваивать время не нужно
                    auth.logout(request)
                    return

            # Записываем время последнего запроса
            request.session[self.session_key] = datetime.datetime.now()


class M3JSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        self.dict_list = kwargs.pop('dict_list', None)
        super(M3JSONEncoder, self).__init__(*args, **kwargs)

    def default(self, obj):
        # обработаем простейшие объекты,
        # которые не обрабатываются стандартным способом
        if isinstance(obj, datetime.datetime):
            return '%02d.%02d.%04d %02d:%02d:%02d' % (
                obj.day, obj.month, obj.year, obj.hour, obj.minute, obj.second)
        elif isinstance(obj, datetime.date):
            return '%02d.%02d.%04d' % (obj.day, obj.month, obj.year)
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M')
        elif isinstance(obj, decimal.Decimal):
            return str(obj)

        # Прошерстим методы и свойства, найдем те,
        # которые могут передаваться на клиента
        # Клонирование словаря происходит потому,
        # что сериализуемые методы переопределяются результатами своей работы
        cleaned_dict = {}
        dict = copy.copy(obj.__dict__)

        # Для джанговских моделей функция dir
        # дополнительно возвращает "ссылки" на связанные модели.
        # Их не нужно сериализовать, а также при обращении к ним
        # происходят запросы к БД. Причем на практике есть случаи,
        # когда эти запросы вызвают эксепешны
        # (например, если изменен id'шник объекта)
        related_objs_attrs = []
        manager_names = []
        if isinstance(obj, dj_models.Model):
            related_objs = ModelOptions(obj).get_all_related_objects()
            related_objs_attrs = [ro.model_name for ro in related_objs]
            # Также соберем все атрибуты-менеджеры (их может быть несколько).
            # Сюда попадет "objects", который исключаем из обработки ниже.
            for attr in obj.__class__.__dict__:
                if isinstance(
                    obj.__class__.__dict__[attr],
                    dj_models.manager.ManagerDescriptor
                ):
                    manager_names.append(attr)

        # если передали специальный список атрибутов, то пройдемся по ним
        # атрибуты вложенных объектов разделены точкой
        # будут созданы вложенные объекты для кодирования
        if self.dict_list:
            for item in self.dict_list:
                lst = item.split('.')
                value = obj
                arr = dict
                last_attr = None
                set_value = False
                for attr in lst:
                    if last_attr:
                        if last_attr not in arr:
                            arr[last_attr] = {}
                        else:
                            if not isinstance(arr[last_attr], type({})):
                                value = None
                                # у объекта уже стоит свойство не словарь,
                                # видимо оно пришло откуда-то свыше
                                set_value = False
                                break
                        arr = arr[last_attr]
                    if hasattr(value, attr):
                        value = getattr(value, attr)
                        if callable(value):
                            # это не свойство а функция, вызовем ее
                            value = value()
                        # нашли свойство, значит его надо будет
                        # поставить после цикла
                        set_value = True
                    else:
                        value = None
                    last_attr = attr
                if set_value:
                    arr[attr] = value

        for attr in dir(obj):
            # Во всех экземплярах моделей Django есть атрибут "objects",
            # т.к. он является статик-атрибутом модели.
            # Но заботливые разработчики джанги позаботились о нас
            # и выкидывают спицифичную ошибку
            # "Manager isn't accessible via %s instances"
            # при обращении из экземпляра.
            # Поэтому "objects" нужно игнорировать.
            # Да и вообще все менеджеры надо игнорировать,
            # т.к. их имена мы собираем выше.
            # Также проигнорируем приватные и протектнутные атрибуты
            if (
                not attr.startswith('_')
                and attr not in manager_names
                and attr != 'tree'
                and attr not in related_objs_attrs
            ):
                try:
                    # если метод или свойство есть в классе,
                    # то проверим у него признак
                    class_attr_value = getattr(obj.__class__, attr, None)
                    if not class_attr_value is None:
                        json_encode = getattr(
                            class_attr_value, 'json_encode', False)
                        if json_encode:
                            value = getattr(obj, attr)
                            if callable(value):
                                # если это метод, то вызовем его
                                dict[attr] = value()
                            else:
                                # иначе это было свойство или какой-то атрибут
                                dict[attr] = value
                except Exception as exc:
                    # Вторая проблема с моделями в том,
                    # что dir кроме фактических полей возвращает ассессоры.
                    # При попытке обратиться к ним происходит запрос(!)
                    # и может возникнуть ошибка DoesNotExist
                    # Заботливые разработчики Django
                    # сделали её разной для всех моделей ;)
                    if exc.__class__.__name__.find('DoesNotExist') == -1:
                        raise

        for attribute in dict.keys():
            # Для полей типа myfield_id автоматически создается атрибут,
            # ссылающияся на наименование, например,
            # для myfield_id будет myfield_ref_name,
            # конечно если у модели myfield есть name.
            # Зачем это нужно - х.з.
            if len(attribute) > 3 and attribute.endswith('_id'):
                try:
                    field_name = attribute[0:len(attribute) - 3]
                    if getattr(getattr(obj, field_name), 'name'):
                        if callable(getattr(getattr(obj, field_name), 'name')):
                            cleaned_dict[field_name + '_ref_name'] = getattr(
                                getattr(obj, field_name), 'name')()
                        else:
                            cleaned_dict[field_name + '_ref_name'] = getattr(
                                getattr(obj, field_name), 'name')
                except:
                    pass
            if len(attribute) > 6 and attribute.endswith('_cache'):
                # вережим этот кусок, т.к. если есть кэш на ForeignKey,
                # то он отработался на верхнем этапе
                # а если кэш на что-то другое (set etc),
                # то фиг знает какое свойство у него надо брать
                pass
            # Ибо нефиг сериализовать protected/private атрибуты!
            if attribute.startswith('_'):
                pass
            else:
                # просто передадим значение,
                # оно будет закодировано в дальнейшем
                cleaned_dict[attribute] = dict[attribute]
        return cleaned_dict


def json_encode(f):
    """
    Декоратор, которым нужно отмечать сериализуемые в M3JSONEncoder методы
    """
    f.json_encode = True
    return f


class property_json_encode(property):
    """
    Декоратор для свойств, которые нужно отмечать сериализуемые в M3JSONEncoder
    """
    json_encode = True


class RelatedError(Exception):
    """
    Исключение для получения связанных объектов
    """
    pass


def authenticated_user_required(f):
    """
    Декоратор проверки того, что к обращение к требуемому ресурсу системы
    производится аутентифицированным пользователем
    """

    def action(request, *args, **kwargs):
        user = request.user
        if not user or not user.is_authenticated():
            if request.is_ajax():
                res = OperationResult.by_message(
                    u'Вы не авторизованы. Возможно, закончилось время '
                    u'пользовательской сессии.<br>'
                    u'Для повторной аутентификации обновите страницу.')
                return res.get_http_response()
            else:
                return HttpResponseRedirect('/')
        else:
            return f(request, *args, **kwargs)

    return action


class PrettyTracebackMiddleware(object):
    """
    Middleware, выводящая traceback'и в html-виде
    """
    def process_exception(self, request, exception):
        reporter = ExceptionReporter(request, *sys.exc_info())
        html = reporter.get_traceback_html()
        return HttpResponseServerError(html, content_type='text/html')
