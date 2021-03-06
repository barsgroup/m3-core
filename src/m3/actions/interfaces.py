#coding:utf-8
'''
Интерфейсы
++++++++++
'''

from abc import ABCMeta, abstractmethod


class ISelectablePack(object):
    """
    Интерфейс pack-классов для выбора значений из полей ExtDictSelectField
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_edit_url(self):
        """ Получить адрес для запроса диалога редактирования
        выбранного элемента """

    @abstractmethod
    def get_autocomplete_url(self):
        """ Получить адрес для запроса элементов подходящих введенному
        в поле тексту """

    @abstractmethod
    def get_select_url(self):
        """ Получить адрес для запроса диалога выбора элемента """

    @abstractmethod
    def get_display_text(self, key, attr_name=None):
        """ Получить отображаемое значение записи (или атрибута attr_name)
        по ключу key """


class IMultiSelectablePack(ISelectablePack):
    """
    Интерфейс pack-классов для множественного выбора значений из
        полей ExtMultiSelectField
    """
    @abstractmethod
    def get_multi_select_url(self):
        """ Получить адрес для запроса диалога множественного
        выбора элемента """

    @abstractmethod
    def get_display_dict(self, key, value_field='id', display_field='name'):
        """
        Получить список словарей, необходимый для представления выбранных
        значений ExtMultiSelectField
        Пример результата: [{'id':0,'name':u''},]
        """
