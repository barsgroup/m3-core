#coding:utf-8
"""
Created on 08.07.2011

@author: kirov
"""

from m3.ui.actions import Action, ActionPack, ACD
from m3.ui.actions.context import ActionContext
from m3.ui.actions.results import OperationResult, ExtUIScriptResult, PreJsonResult
from m3.ui.actions.utils import extract_int
from m3.helpers.dataprovider import GetRecordsParams, BaseRecordProvider, BaseRecord

class BaseRecordPack(ActionPack):
    """
    Экшенпак для работы с провайдерами записей
    """
    # Провайдер записей, наследованный от BaseRecordProvider
    provider = None

    # Имя идентификатора записи в контексте
    context_id = 'id'

    # Имя идентификатора мастер-записи в контексте
    context_master_id = None
    # Имя поля мастер-записи в записи
    master_id = None

    # Форма, которая будет вызываться при редактировании записи
    edit_window = None
    # Форма, которая будет вызываться при создании новой записи
    new_window = None
    
    # Карта соответствия контекстных данных и имен атрибутов объекта (для фильтров и сортировки)
    # например:
    #    'sum': 'sum'
    # или:
    #    'date': {'attr': 'person__birthday', 'oper': 'icontains'}
    context_attr_map = {}
    
    def __init__(self, *args, **kwargs):
        super(BaseRecordPack, self).__init__(*args, **kwargs)
        self.action_edit = RecordEditWindowAction()
        self.action_delete = RecordDeleteAction()
        self.action_rows = RecordRowsAction()
        self.action_save = RecordSaveAction()

        self.actions.extend([
            self.action_edit, self.action_delete, self.action_rows, 
            self.action_save
        ])

    #====================== Описание контекста действий =======================

    def _get_edit_action_context_declaration(self):
        if self.context_master_id:
            return [
                ACD(name=self.context_master_id, required=True, type=int, verbose_name=u'id мастер-записи'),
                ACD(name=self.context_id, required=True, type=int, default=0, verbose_name=u'id записи в гриде'),
                ACD(name='isGetData', default=False, type=bool, required=True, verbose_name = u'признак загрузки данных')
            ]
        else:
            return [
                ACD(name=self.context_id, required=True, type=int, default=0, verbose_name=u'id записи в гриде'),
                ACD(name='isGetData', default=False, type=bool, required=True, verbose_name = u'признак загрузки данных')
            ]

    def _get_save_action_context_declaration(self):
        if self.context_master_id:
            return [
                ACD(name=self.context_master_id, required=True, type=int, verbose_name=u'id мастер-записи'),
                ACD(name=self.context_id, required=True, type=int, default=0, verbose_name=u'id записи в гриде')
            ]
        else:
            return [
                ACD(name=self.context_id, required=True, type=int, default=0, verbose_name=u'id записи в гриде')
            ]
            
    def _get_rows_action_context_declaration(self):
        if self.context_master_id:
            return [
                ACD(name=self.context_master_id, required=True, type=int, verbose_name=u'id мастер-записи')
            ]
        else:
            return []

    def _get_delete_action_context_declaration(self):
        return [
            ACD(name=self.context_id, required=True, type=ActionContext.ValuesList(), verbose_name=u'Список id удаляемых элементов')
        ]
    
    #====================== Работа с провайдером =======================
    
    def get_provider(self, request, context):
        """
        Получение провайдера данных
        """
        assert isinstance(self.provider, BaseRecordProvider), 'provider должен быть классом от BaseRecordProvider'
        return self.provider
    
    def get_row(self, request, context, is_new, id=None):
        """
        Создание новой/получение записи по id
        """
        if is_new:
            return self.get_provider(request, context).new_record()
        else:
            return self.get_provider(request, context).get_record(id)
    
    def get_rows(self, request, context, params):
        """
        Получение списка записей
        """
        assert isinstance(params, GetRecordsParams)
        return self.get_provider(request, context).get_records(params)

    def save_row(self, request, context, record, is_new):
        """
        Сохранение записи
        """
        assert isinstance(record, BaseRecord), 'record должен быть классом от BaseRecord'
        record.save()
    
    def validate_row(self, request, context, record, is_new):
        """
        Проверка записи на корректность заполнения
        """
        assert isinstance(record, BaseRecord), 'record должен быть классом от BaseRecord'
        return record.validate()
    
    def delete_rows(self, request, context, ids):
        """
        Удаление записи по id
        """
        self.get_provider(request, context).delete_records(ids)
    
    #==================== Получение адресов экшенов =====================    
    def get_edit_url(self):
        '''
        Возвращает адрес формы редактирования элемента справочника.
        '''
        return self.action_edit.get_absolute_url()
    
    def get_rows_url(self):
        '''
        Возвращает адрес по которому запрашиваются элементы грида
        '''
        return self.action_rows.get_absolute_url()
    
    #====================== Работа с окнами =======================
    
    def get_edit_window(self, request, context, record, is_new):
        """
        Получение окна редактирования записи
        """
        if is_new:
            assert self.new_window, 'new_window должен быть задан'
            return self.new_window(create_new=is_new)
        else:
            assert self.edit_window, 'edit_window должен быть задан'
            return self.edit_window(create_new=is_new)
    
    def update_context(self, request, context, window):
        """
        Настройка контекста окна
        """
        if not window.action_context:
            window.action_context = context
        else:
            window.action_context.__dict__.update(context.__dict__)
    
    def bind_record_to_window(self, request, context, record, window, is_new):
        """
        Отображение записи на форму
        """
        window.form.from_object(record)
        
    def bind_request_to_window(self, request, context, window):
        """
        Отображение запроса на форму
        """
        window.form.bind_to_request(request)
    
    def bind_window_to_record(self, request, context, window, record, is_new):
        """
        Отображение формы в запись
        """
        window.form.to_object(record)
        
    def bind_to_grid(self, request, context, grid):
        """
        Присоединение списка к гриду
        """
        if not grid.get_store:
            grid_store = ExtJsonStore(url=self.action_rows.get_absolute_url(), auto_load=True, remote_sort=True)
            grid_store.total_property = 'total'
            grid_store.root = 'rows'
            grid.set_store(grid_store)
        else:
            grid.store.url = self.action_rows.get_absolute_url()
            grid.store.total_property = 'total'
            grid.store.root = 'rows'
        
        grid.url_new = self.action_edit.get_absolute_url()
        grid.url_edit = self.action_edit.get_absolute_url()
        grid.url_delete = self.action_delete.get_absolute_url()
        grid.url_data = self.action_rows.get_absolute_url()
        
        grid.row_id_name = self.context_id
    
    #====================== Обработка запросов =======================
        
    def edit_window_request(self, request, context):
        """
        Запрос на создание формы редактирования/нового элемента
        """
        row_id = getattr(context, self.context_id)
        if row_id:
            is_new = False
        else:
            is_new = True
        obj = self.get_row(request, context, is_new, row_id)
        win = self.get_edit_window(request, context, obj, is_new)
        self.bind_record_to_window(request, context, obj, win, is_new)
        
        is_get_data = context.isGetData
        if not is_get_data: 
            win.form.url = self.action_save.get_absolute_url()
            win.data_url = self.action_edit.get_absolute_url()
            self.update_context(request, context, win)
            
            return ExtUIScriptResult(win)
        else:
            # выжмем данные из окна обратно в отдельный объект,
            # т.к. в окне могли быть и другие данных (не из этого объекта)
            data_object = {}
            # т.к. мы не знаем какие поля должны быть у объекта - создадим все, которые есть на форме
            all_fields = win.form._get_all_fields(win)
            for field in all_fields:
                data_object[field.name] = None
            self.bind_window_to_record(request, context, win, data_object)
            
            return PreJsonResult({'success': True, 'data': data_object})

    def save_request(self, request, context):
        """
        Запрос на сохранение редактированной/новой записи
        """
        row_id = getattr(context, self.context_id)
        if row_id:
            is_new = False
        else:
            is_new = True
        obj = self.get_row(request, context, is_new, row_id)
        win = self.get_edit_window(request, context, obj, is_new)
        self.bind_request_to_window(request, context, win)
        self.bind_window_to_record(request, context, win, obj, is_new)
        result = self.validate_row(request, context, obj, is_new)
        if result:
            return result
        self.save_row(request, context, obj, is_new)
        return OperationResult()
    
    def extract_filter_context(self, request, context):
        """
        В соответствии с настройкой вытащим фильтры
        """
        filter = {}
        for context_name, conf in self.context_attr_map.items():
            filter_word = request.REQUEST.get(context_name)
            if filter_word:
                name = None
                if isinstance(conf, (dict)):
                    if 'attr' in conf:
                        name = conf['attr']
                        if 'oper' in conf:
                            name += '__'+conf['oper']
                elif isinstance(conf, str):
                    name = conf
                if name:
                    filter[name] = filter_word
        return filter
    
    def extract_sort_context(self, request, context):
        """
        В соответствии с настройкой вытащим сортировку
        """
        # TODO: пока обрабатывается только одно поле сортировки
        sorting = {}
        direction = request.REQUEST.get('dir')
        user_sort = request.REQUEST.get('sort')
        if user_sort:
            if user_sort in self.context_attr_map:
                if isinstance(conf, (dict)):
                    if 'attr' in conf:
                        user_sort = conf['attr']
                elif isinstance(conf, str):
                    user_sort = conf
            sorting[user_sort] = direction
        return sorting
    
    def rows_request(self, request, context):
        """
        Запрос на получение списка записей
        """
        params = GetRecordsParams()
        if self.context_master_id:
            master_id = getattr(context, self.context_master_id)
            params.filter[self.master_id] = master_id
        params.begin = extract_int(request, 'start')
        params.end = params.begin + extract_int(request, 'limit')
        filter_context = self.extract_filter_context(request, context)
        params.filter.update(filter_context)
        sort_context = self.extract_sort_context(request, context)
        params.sorting.update(sort_context)
        result = self.get_rows(request, context, params)
        return PreJsonResult(result)

    def delete_rows_request(self, request, context):
        """
        Запрос на удаление записей
        """
        rows_id = getattr(context, self.context_id)
        self.delete_rows(request, context, rows_id)
        return OperationResult()


class RecordEditWindowAction(Action):
    """
    Экшен отдающий форму редактирования записи
    """
    url = '/edit'

    def context_declaration(self):
        return self.parent._get_edit_action_context_declaration()

    def run(self, request, context):
        return self.parent.edit_window_request(request, context)

class RecordSaveAction(Action):
    """
    Экшен отвечает за сохранение записей в гриде
    """
    url = '/save'

    def context_declaration(self):
        return self.parent._get_save_action_context_declaration()

    def run(self, request, context):
        return self.parent.save_request(request, context)

class RecordRowsAction(Action):
    """
    Экшен отвечает за отдачу данных в грид
    """
    url = '/rows'

    def context_declaration(self):
        return self.parent._get_rows_action_context_declaration()

    def run(self, request, context):
        return self.parent.rows_request(request, context)

class RecordDeleteAction(Action):
    """
    Экшен удаляющий записи из грида
    """
    url = '/delete'

    def context_declaration(self):
        return self.parent._get_delete_action_context_declaration()

    def run(self, request, context):
        return self.parent.delete_rows_request(request, context)

    
class BaseRecordListPack(BaseRecordPack):
    # Форма, которая будет вызываться при показе списка
    list_window = None
    # Форма, которая будет вызываться при выборе из списка
    select_window = None
    
    def __init__(self, *args, **kwargs):
        super(BaseRecordListPack, self).__init__(*args, **kwargs)
        self.action_list = RecordListWindowAction()
        self.action_select = RecordSelectWindowAction()
        self.actions.extend([self.action_list, self.action_select])

    #====================== Описание контекста действий =======================
    
    def _get_list_action_context_declaration(self):
        if self.context_master_id:
            return [
                ACD(name=self.context_master_id, required=True, type=int, verbose_name=u'id мастер-записи')
            ]
        else:
            return []
    
    def _get_select_action_context_declaration(self):
        if self.context_master_id:
            return [
                ACD(name=self.context_master_id, required=True, type=int, verbose_name=u'id мастер-записи')
            ]
        else:
            return []
    
    #==================== ФУНКЦИИ ВОЗВРАЩАЮЩИЕ АДРЕСА =====================    
    def get_list_url(self):
        '''
        Возвращает адрес формы списка элементов справочника. 
        Используется для присвоения адресов в прикладном приложении.
        '''
        return self.action_list.get_absolute_url()
    
    def get_select_url(self):
        '''
        Возвращает адрес формы списка элементов справочника. 
        Используется для присвоения адресов в прикладном приложении.
        '''
        return self.action_select.get_absolute_url()
    
    #====================== Работа с окнами =======================
    def get_list_window(self, request, context, is_select):
        if is_select:
            assert self.select_window, 'Attribute "select_window" must be defined!'
            return self.select_window(mode=0)
        else:
            assert self.list_window, 'Attribute "list_window" must be defined!'
            return self.list_window(mode=1)
    
    #====================== Обработка запросов =======================
    
    def list_window_request(self, request, context):
        """
        Отвечает за создание формы списка записей
        """
        win = self.get_list_window(request, context, False)
        self.bind_to_grid(request, context, win.grid)
        
        return ExtUIScriptResult(win)
    
    def select_window_request(self, request, context):
        """
        Отвечает за создание формы выбора записи
        """
        win = self.get_list_window(request, context, True)
        self.bind_to_grid(request, context, win.grid)
        
        return ExtUIScriptResult(win)

class RecordListWindowAction(Action):
    """
    Экшен отдающий форму списка записей
    """
    url = '/list'

    def context_declaration(self):
        return self.parent._get_list_action_context_declaration()

    def run(self, request, context):
        return self.parent.list_window_request(request, context)
    
class RecordSelectWindowAction(Action):
    """
    Экшен отдающий форму выбора записей
    """
    url = '/select'

    def context_declaration(self):
        return self.parent._get_select_action_context_declaration()

    def run(self, request, context):
        return self.parent.select_window_request(request, context)