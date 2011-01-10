#coding:utf-8
'''
Created on 3.3.2010

@author: prefer
'''
from django.conf import settings
from django.utils.datastructures import SortedDict

from m3.ui.ext.base import ExtUIComponent, BaseExtComponent
from base import BaseExtPanel

#===============================================================================
#
#===============================================================================
class ExtPivotGrid(BaseExtPanel):
    '''
    Сводная таблица
    '''

    def __init__(self,*args, **kwargs):
        super(ExtPivotGrid, self).__init__(*args,**kwargs)
        self.template = 'ext-grids/ext-pivot-grid.js'
        self.__store = None
        self.aggregator = None
        self.renderer = None
        self.measure = None
        self._left_axis = []
        self._top_axis = []
        self._items = []
        self.__cm = None
        self.col_model = ExtGridDefaultColumnModel()
        self.force_fit = True
        self.auto_fill = True
        self.__view = None
        self._view_config = {}
        self.init_component(*args,**kwargs)

    def t_render_store(self):
        return self.__store.render([col.data_index for col in self.columns])

    def t_render_columns(self):
        return self.t_render_items()

    def add_column(self, **kwargs):
        self.columns.append(ExtGridColumn(**kwargs))

    def add_left_axis(self, **kwargs):
        self.left_axis.append(ExtPivotGridAxis(**kwargs))

    def add_top_axis(self, **kwargs):
        self.top_axis.append(ExtPivotGridAxis(**kwargs))

    def render_base_config(self):
        super(ExtPivotGrid, self).render_base_config()
        self._view_config['forceFit'] = self.force_fit
        self._view_config['autoFill'] = self.auto_fill
        self._put_config_value('store',self.t_render_store,self.get_store())
        self._put_config_value('measure',self.measure)
        self._put_config_value('aggregator',self.aggregator)
        self._put_config_value('renderer',self.renderer)
        self._put_config_value('leftAxis',self.t_render_left_axis)
        self._put_config_value('topAxis',self.t_render_top_axis)

        self._put_config_value('colModel', self.col_model.render)
        self._put_config_value('view', self.t_render_view, self.view)
        self._put_config_value('viewConfig', self._view_config)

    @property
    def columns(self):
        return self._items

    @property
    def left_axis(self):
        return self._left_axis

    @property
    def top_axis(self):
        return self._top_axis

    @property
    def view(self):
        return self.__view

    @view.setter
    def view(self, value):
        self.__view = value

    def render(self):
        self.render_base_config()
        self.render_params()
        config = self._get_config_str()
        params = self._get_params_str()
        return 'new Ext.grid.PivotGrid({%s}, {%s})' % (config, params)

    def set_store(self, store):
        self.__store = store

    def get_store(self):
        return self.__store

    store = property(get_store, set_store)

    @property
    def col_model(self):
        return self.__cm

    @col_model.setter
    def col_model(self, value):
        self.__cm = value
        self.__cm.grid = self

    def t_render_view(self):
        return self.view.render()

    def t_render_left_axis(self):
        return '[%s]' % ','.join(['''{
            dataIndex:"%s",
            header:"%s",
            width:%d,
            defaultHeaderWidth:%d,
            orientation:"%s"
        }'''  % (
            axe.data_index,
            axe.header,
            axe.width,
            axe.default_header_width,
            axe.orientation
        ) for axe in self.left_axis])

    def t_render_top_axis(self):
        return '[%s]' % ','.join(['''{
            dataIndex:"%s",
            header:"%s",
            width:%d,
            defaultHeaderWidth:%d,
            orientation:"%s"
        }'''  % (
            axe.data_index,
            axe.header,
            axe.width,
            axe.default_header_width,
            axe.orientation
        ) for axe in self.top_axis])

#===============================================================================
# Компонент таблица, или grid
class ExtGrid(BaseExtPanel):
    '''
    Таблица

    @version: 0.1
    @begin_designer
    {title: "Grid"
    ,ext_class: "Ext.grid.GridPanel"
    ,xtype: "grid"
    ,attr: [{
        ext_attr: "loadMask"
        ,py_attr: "load_mask"
    },{
        ext_attr: "enableDragDrop"
        ,py_attr: "drag_drop"
    },{
        ext_attr: "ddGroup"
        ,py_attr: "drag_drop"
    },{
        ext_attr: "enableDragDrop"
        ,py_attr: "drag_drop_group"
    },{
        ext_attr: "sm"
        ,py_attr: "sm"
    },{
        ext_attr: "view"
        ,py_attr: "view"
    },{
        ext_attr: "autoExpandColumn"
        ,py_attr: "auto_expand_column"
    }]}
    @end_designer
    '''
    def __init__(self, *args, **kwargs):
        super(ExtGrid, self).__init__(*args, **kwargs)
        self.template = 'ext-grids/ext-grid.js'
        self._items = []
        self.__store = None
        self.editor = False
        self.load_mask = False
        self.drag_drop = False
        self.drag_drop_group = None
        self.force_fit = True
        # selection model
        self.__sm = None
        # view
        self.__view = None
        # Колонка для авторасширения
        self.auto_expand_column = None
        # устанавливается True, если sm=CheckBoxSelectionModel. Этот флаг нужен
        # чтобы знать когда нужен дополнительный column
        self.__checkbox = False
        # перечень плугинов
        self.plugins = []
        # модель колонок
        self.__cm = None
        self.col_model = ExtGridDefaultColumnModel()
        self._view_config = {}
        self.show_preview = False
        self.enable_row_body = False
        self.get_row_class = None
        self.column_lines = True # признак отображения вертикальных линий в гриде
        self.read_only = False #Если True не рендерим drag and drop, выключаем editor
        self.label = None

        self.init_component(*args, **kwargs)

        # protected
        self.show_banded_columns = False
        self.banded_columns = SortedDict()

    def t_render_plugins(self):
        return '[%s]' % ','.join(self.plugins)

    def t_render_banded_columns(self):
        '''
        Возвращает JS массив состоящий из массивов с описанием объединенных
        колонок. Каждый вложенный массив соответствует уровню шапки грида от
        верхней к нижней.
        '''
        result = []
        for level_list in self.banded_columns.values():
            result.append('[%s]' % ','.join([ column.render() \
                                             for column in level_list ]))
        return '[%s]' % ','.join(result)

    def t_render_columns(self):
        return self.t_render_items()

    def t_render_store(self):
        assert self.__store, 'Store is not define'
        return self.__store.render([column.data_index for column in self.columns])

    def add_column(self, **kwargs):
        self.columns.append(ExtGridColumn(**kwargs))

    def add_bool_column(self, **kwargs):
        self.columns.append(ExtGridBooleanColumn(**kwargs))

    def add_number_column(self, **kwargs):
        self.columns.append(ExtGridNumberColumn(**kwargs))

    def add_date_column(self, **kwargs):
        self.columns.append(ExtGridDateColumn(**kwargs))

    def add_banded_column(self, column, level, colspan):
        '''
        Добавляет в грид объединенную ячейку.
        @param column: Колонка грида (ExtGridColumn)
        @param colspan: Количество колонок которые находятся
            под данной колонкой (int)
        @param level: Уровень учейки где 0 - самый верхний, 1-ниже, и т.д. (int)

        upd:26.10.2010 kirov
        колонка может быть не указана, т.е. None, в этом случае на указанном уровне будет "дырка"
        '''
        class BlankBandColumn():
            colspan = 0
            def render(self):
                return '{%s}' % (('colspan:%s' % self.colspan) if self.colspan else '')

        assert isinstance(level, int)
        assert isinstance(colspan, int)
        assert isinstance(column, ExtGridColumn) or not column
        if not column:
            column = BlankBandColumn()
        # Колонки хранятся в списках внутки сортированного словаря,
        #чтобы их можно было
        # извечь по возрастанию уровней
        column.colspan = colspan
        level_list = self.banded_columns.get(level, [])
        level_list.append(column)
        self.banded_columns[level] = level_list
        self.show_banded_columns = True

    def clear_banded_columns(self):
        '''
        Удаляет все объединенные колонки из грида
        '''
        self.banded_columns.clear()
        self.show_banded_columns = False

    def set_store(self, store):
        self.__store = store

    def get_store(self):
        return self.__store

    store = property(get_store, set_store)

    def make_read_only(self, access_off=True, exclude_list=[], *args, **kwargs):
        # Описание в базовом классе ExtUiComponent.
        # Обрабатываем исключения.
        access_off = self.pre_make_read_only(access_off, exclude_list, 
                                             *args, **kwargs)
        # Выключаем\включаем компоненты.
        super(ExtGrid, self).make_read_only(access_off, exclude_list, 
                                            *args, **kwargs)
        self.read_only = access_off
        if self.columns:
            for column in self.columns:
                column.make_read_only(self.read_only, exclude_list, 
                                                    *args, **kwargs)
        # контекстное меню.
        context_menu_items = [self.handler_contextmenu, 
                              self.handler_rowcontextmenu]
        for context_menu in context_menu_items:
            if (context_menu and
                hasattr(context_menu,'items') and
                context_menu.items and
                hasattr(context_menu.items,'__iter__')):
                for item in context_menu.items:
                    if isinstance(item, ExtUIComponent):
                        item.make_read_only(self.read_only, 
                                            exclude_list, 
                                            *args, **kwargs)
            

    @property
    def columns(self):
        return self._items

    @property
    def sm(self):
        return self.__sm

    @sm.setter
    def sm(self, value):
        self.__sm = value
        self.checkbox_model = isinstance(self.__sm, ExtGridCheckBoxSelModel)

    @property
    def view(self):
        return self.__view

    @view.setter
    def view(self, value):
        self.__view = value

    def t_render_view(self):
        return self.view.render()

    def pre_render(self):
        super(ExtGrid, self).pre_render()
        if self.store:
            self.store.action_context = self.action_context

    @property
    def col_model(self):
        return self.__cm

    @col_model.setter
    def col_model(self, value):
        self.__cm = value
        self.__cm.grid = self

    #//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\
    # Врапперы над событиями listeners[...]
    #------------------------------------------------------------------------
    @property
    def handler_click(self):
        return self._listeners.get('click')

    @handler_click.setter
    def handler_click(self, function):
        self._listeners['click'] = function

    @property
    def handler_dblclick(self):
        return self._listeners.get('dblclick')

    @handler_dblclick.setter
    def handler_dblclick(self, function):
        self._listeners['dblclick'] = function

    @property
    def handler_contextmenu(self):
        return self._listeners.get('contextmenu')

    @handler_contextmenu.setter
    def handler_contextmenu(self, menu):
        menu.container = self
        self._listeners['contextmenu'] = menu

    @property
    def handler_rowcontextmenu(self):
        return self._listeners.get('rowcontextmenu')

    @handler_rowcontextmenu.setter
    def handler_rowcontextmenu(self, menu):
        menu.container = self
        self._listeners['rowcontextmenu'] = menu

    #----------------------------------------------------------------------------

    def render_base_config(self):
        super(ExtGrid, self).render_base_config()
        if self.force_fit:
            self._view_config['forceFit'] = self.force_fit
        if self.show_preview:
            self._view_config['showPreview'] = self.show_preview
        if self.enable_row_body:
            self._view_config['enableRowBody'] = self.enable_row_body
        if self.get_row_class:
            self._view_config['getRowClass'] = self.get_row_class
        self._put_config_value('stripeRows', True)
        self._put_config_value('stateful', True)
        self._put_config_value('loadMask', self.load_mask)
        self._put_config_value('autoExpandColumn', self.auto_expand_column)
        if not self.read_only:
            self._put_config_value('enableDragDrop', self.drag_drop)
            self._put_config_value('ddGroup', self.drag_drop_group)
        self._put_config_value('editor', self.editor)
        self._put_config_value('view', self.t_render_view, self.view)
        self._put_config_value('store', self.t_render_store, self.get_store())
        self._put_config_value('viewConfig', self._view_config)
        self._put_config_value('columnLines', self.column_lines, self.column_lines)
        if self.label:
            self._put_config_value('fieldLabel', self.label)

    def render_params(self):
        super(ExtGrid, self).render_params()

        handler_cont_menu = self.handler_contextmenu.render \
                        if self.handler_contextmenu else ''

        handler_rowcontextmenu = self.handler_rowcontextmenu.render \
                        if self.handler_rowcontextmenu else ''

        self._put_params_value('menus', {'contextMenu': handler_cont_menu,
                                         'rowContextMenu': handler_rowcontextmenu})
        if self.sm:
            self._put_params_value('selModel', self.sm.render)

        self._put_params_value('colModel', self.col_model.render)
        self._put_params_value('plugins', self.t_render_plugins)

        if self.show_banded_columns:
            self._put_params_value('bundedColumns', self.t_render_banded_columns)

    def render(self):
        try:
            self.pre_render()

            self.render_base_config()
            self.render_params()
        except Exception as msg:
            raise Exception(msg)


        config = self._get_config_str()
        params = self._get_params_str()
        return 'createGridPanel({%s}, {%s})' % (config, params)


#===============================================================================
# Оси к пивот гриду
#===============================================================================

class ExtPivotGridAxis(ExtUIComponent):
    DEFAULT_HEADER_WIDTH = 100

    def __init__(self,*args, **kwargs):
        super(ExtPivotGridAxis,self).__init__(*args,**kwargs)
        self.width = ExtPivotGridAxis.DEFAULT_HEADER_WIDTH
        self.data_index = None
        self.orientation = 'horizontal'
        self.header = None
        self.default_header_width = 80
        self.init_component(*args, **kwargs)


#===============================================================================
# Колонки к гриду
class BaseExtGridColumn(ExtUIComponent):
    GRID_COLUMN_DEFAULT_WIDTH = 100
    THOUSAND_CURRENCY_RENDERER = 'thousandCurrencyRenderer'

    def __init__(self, *args, **kwargs):
        super(BaseExtGridColumn, self).__init__(*args, **kwargs)
        self.header = None
        self.sortable = False
        self.data_index = None
        self.align = None
        self.width = BaseExtGridColumn.GRID_COLUMN_DEFAULT_WIDTH
        self.editor = None
        self._column_renderer = []
        self.tooltip = None
        self.hidden = False
        self.read_only = False
        self.colspan = None
        # дополнительные атрибуты колонки
        self.extra = {}

    def t_render_extra(self):
        lst = []
        for key in self.extra.keys():
            val = self.extra[key]

            if isinstance(val,BaseExtComponent):
                lst.append('%s:%s' % (key,val.render()))
            elif isinstance(val,bool):
                lst.append('%s:%s' % (key,str(val).lower()))
            elif isinstance(val, (int,str,unicode)):
                lst.append('%s:%s' % (key,val))
            else: # пусть как хочет так и рендерится
                lst.append('%s:%s' % (key,val))
        print lst
        return ','.join(lst)

    def render_editor(self):
        return self.editor.render()

    def make_read_only(self, access_off=True, exclude_list=[], *args, **kwargs):
        # Описание в базовом классе ExtUiComponent.
        # Обрабатываем исключения.
        access_off = self.pre_make_read_only(access_off, exclude_list, *args, **kwargs)
        self.read_only = access_off
        if self.editor and isinstance(self.editor, ExtUIComponent):
            self.editor.make_read_only(self.read_only, exclude_list, *args, **kwargs)
        
    def render_base_config(self):
        super(BaseExtGridColumn, self).render_base_config()
        self._put_config_value('header', self.header)
        self._put_config_value('sortable', self.sortable)
        self._put_config_value('dataIndex', self.data_index)
        self._put_config_value('align', self.align)
        self._put_config_value('editor', self.editor.render if self.editor else None)
        self._put_config_value('hidden', self.hidden)
        self._put_config_value('readOnly', self.read_only)
        self._put_config_value('colspan', self.colspan)
        
        for i, render in enumerate(self._column_renderer):
            if BaseExtGridColumn.THOUSAND_CURRENCY_RENDERER == render:
                #Финансовый формат для Сумм и Цен подразумевает прижимание к правому краю.             
                thousand_column_renderer = \
                '(function(val, metaData){ metaData.attr="style=text-align:right"; return %s.apply(this, arguments);}) ' \
                    % BaseExtGridColumn.THOUSAND_CURRENCY_RENDERER
                    
                self._column_renderer[i] = thousand_column_renderer
            
        self._put_config_value('renderer', self.render_column_renderer)
        self._put_config_value('tooltip', self.tooltip)
        
    @property
    def column_renderer(self):
        return ','.join(self._column_renderer)
    
    @column_renderer.setter
    def column_renderer(self, value):
        self._column_renderer.append(value)
        
    def render_column_renderer(self):
        '''
        Кастомный рендеринг функций-рендерера колонок
        '''
        if self._column_renderer:
            self._column_renderer.reverse()
            val =  self._get_renderer_func(self._column_renderer)
            return  'function(val, metaData, record, rowIndex, colIndex, store){return %s}' % val
        return None
    
    def _get_renderer_func(self, list_renderers):        
        '''
        Рекурсивная функция, оборачивающая друг в друга рендереры колонок
        '''
        if list_renderers:            
            return '%s(%s, metaData, record, rowIndex, colIndex, store)' \
                % (list_renderers[0], self._get_renderer_func(list_renderers[1:]) )
        else:
            return 'val'
        
        
#===============================================================================
class ExtGridColumn(BaseExtGridColumn):
    def __init__(self, *args, **kwargs):
        super(ExtGridColumn, self).__init__(*args, **kwargs)
        #self.template = 'ext-grids/ext-grid-column.js'
        self.init_component(*args, **kwargs)

    def render(self):
        try:
            self.render_base_config()            
        except Exception as msg:
            raise Exception(msg)
        
        config = self._get_config_str()        
        extra = self.t_render_extra()
        return '{%s}' % (config + ',' + extra if extra else config)    

#===============================================================================
class ExtGridBooleanColumn(BaseExtGridColumn):
    def __init__(self, *args, **kwargs):
        super(ExtGridBooleanColumn, self).__init__(*args, **kwargs)
        self.template = 'ext-grids/ext-bool-column.js'
        self.text_false = None
        self.text_true = None
        self.text_undefined = None
        self.init_component(*args, **kwargs)

#===============================================================================
class ExtGridNumberColumn(BaseExtGridColumn):
    def __init__(self, *args, **kwargs):
        super(ExtGridNumberColumn, self).__init__(*args, **kwargs)
        self.template = 'ext-grids/ext-number-column.js'
        self.format = None
        self.init_component(*args, **kwargs)

#===============================================================================
class ExtGridDateColumn(BaseExtGridColumn):
    def __init__(self, *args, **kwargs):
        super(ExtGridDateColumn, self).__init__(*args, **kwargs)
        self.template = 'ext-grids/ext-date-column.js'
        try:
            self.format = settings.DATE_FORMAT.replace('%', '')
        except:
            self.format = 'd.m.Y'
        self.init_component(*args, **kwargs)

#==============================================================================
# Column Model для грида
class BaseExtGridSelModel(BaseExtComponent):
    def __init__(self, *args, **kwargs):
        super(BaseExtGridSelModel, self).__init__(*args, **kwargs)

#===============================================================================
class ExtGridCheckBoxSelModel(BaseExtGridSelModel):
    def __init__(self, *args, **kwargs):
        super(ExtGridCheckBoxSelModel, self).__init__(*args, **kwargs)
        self.single_select = False
        self.init_component(*args, **kwargs)

    def render(self):
        single_sel = 'singleSelect: true' if self.single_select else ''
        return 'new Ext.grid.CheckboxSelectionModel({ %s })' % single_sel

#===============================================================================
class ExtGridRowSelModel(BaseExtGridSelModel):
    def __init__(self, *args, **kwargs):
        super(ExtGridRowSelModel, self).__init__(*args, **kwargs)
        self.single_select = False
        self.init_component(*args, **kwargs)

    def render(self):
        single_sel = 'singleSelect: true' if self.single_select else ''
        return 'new Ext.grid.RowSelectionModel({ %s })' % single_sel

#===============================================================================
class ExtGridCellSelModel(BaseExtGridSelModel):
    def __init__(self, *args, **kwargs):
        super(ExtGridCellSelModel, self).__init__(*args, **kwargs)
        self.init_component(*args, **kwargs)

    def render(self):
        return 'new Ext.grid.CellSelectionModel()'

#===============================================================================
class ExtGridDefaultColumnModel(BaseExtComponent):
    def __init__(self, *args, **kwargs):
        super(ExtGridDefaultColumnModel, self).__init__(*args, **kwargs)
        self.grid = None
        self.init_component(*args, **kwargs)

    def render(self):
        return 'new Ext.grid.ColumnModel({columns:%s})' % self.grid.t_render_columns()

#===============================================================================
class ExtGridLockingColumnModel(BaseExtComponent):
    def __init__(self, *args, **kwargs):
        super(ExtGridLockingColumnModel, self).__init__(*args, **kwargs)
        self.grid = None
        self.init_component(*args, **kwargs)

    def render(self):
        return 'new Ext.ux.grid.LockingColumnModel({columns:%s})' % self.grid.t_render_columns()

#===============================================================================
class ExtGridLockingHeaderGroupColumnModel(BaseExtComponent):
    def __init__(self, *args, **kwargs):
        super(ExtGridLockingHeaderGroupColumnModel, self).__init__(*args, **kwargs)
        self.grid = None
        self.init_component(*args, **kwargs)

    def render(self):
        return 'new Ext.ux.grid.LockingGroupColumnModel({columns:%s})' % self.grid.t_render_columns()

#===============================================================================
# Компонент - расширенное дерево, включающее колонки, с возможностью добавлять
# view и column model
class ExtAdvancedTreeGrid(ExtGrid):
    '''
    Расширенное дерево на базе Ext.ux.maximgb.TreeGrid
    '''
    def __init__(self, *args, **kwargs):
        super(ExtAdvancedTreeGrid, self).__init__(*args, **kwargs)
        self.template = 'ext-grids/ext-advanced-treegrid.js'
        self.url = None
        self.master_column_id = None

        # Свойства для внутреннего store:
        self.store_root = 'rows'

        # Свойства для внутеннего bottom bara:
        self.use_bbar = False
        self.bbar_page_size = 10

        self.init_component(*args, **kwargs)

    def t_render_columns_to_record(self):
        return '[%s]' % ','.join(['{name:"%s"}'  % col.data_index \
                                  for col in self.columns])

    def add_column(self, **kwargs):
        # FIXME: Хак, с сгенерированным client_id компонент отказывается работать
        if kwargs.get('data_index'):
            kwargs['client_id'] = kwargs.get('data_index')
        super(ExtAdvancedTreeGrid, self).add_column(**kwargs)

    def render_base_config(self):
        super(ExtAdvancedTreeGrid, self).render_base_config()
        self._put_config_value('master_column_id', self.master_column_id)

    def render_params(self):
        super(ExtAdvancedTreeGrid, self).render_params()
        self._put_params_value('storeParams', {'url': self.url,
                                               'root': self.store_root})

        self._put_params_value('columnsToRecord', self.t_render_columns_to_record)

        if self.use_bbar:
            self._put_params_value('bbar', {'pageSize': self.bbar_page_size})

    def t_render_base_config(self):
        return self._get_config_str()

    def render(self):
        self.render_base_config()
        self.render_params()

        base_config = self._get_config_str()
        params = self._get_params_str()
        return 'createAdvancedTreeGrid({%s},{%s})' %(base_config, params)

#===============================================================================
# Компоненты view для грида
class ExtGridGroupingView(BaseExtComponent):
    '''
    Компонент используемый при группировке
    '''
    def __init__(self, *args, **kwargs):
        super(ExtGridGroupingView, self).__init__(*args, **kwargs)
        self.force_fit = True
        self.show_preview = False
        self.enable_row_body = False
        self.get_row_class = None
        self.group_text_template = '{text} ({[values.rs.length]})'
        self.init_component(*args, **kwargs)

    def render_params(self):
        super(ExtGridGroupingView, self).render_params()
        if self.force_fit:
            self._put_params_value('forceFit', self.force_fit)
        if self.show_preview:
            self._put_params_value('showPreview', self.show_preview)
        if self.enable_row_body:
            self._put_params_value('enableRowBody', self.enable_row_body)
        if self.get_row_class:
            self._put_params_value('getRowClass', self.get_row_class)
        self._put_params_value('groupTextTpl', self.group_text_template)

    def render(self):
        try:
            self.pre_render()
            self.render_base_config()
            self.render_params()
        except Exception as msg:
            raise Exception(msg)
        params = self._get_params_str()
        return 'new Ext.grid.GroupingView({%s})' % (params)

    # если требуется вывести какое-либо слово после количества, шаблон должен
    #иметь след вид:
    # 'group_text_tpl': """groupTextTpl:'{text} ({[values.rs.length]}
    #    {[values.rs.length > 1 ? "Объекта" : "Объект"]})'"""
    # но проблемы с обработкой двойных кавычек

#===============================================================================
class ExtGridLockingView(BaseExtComponent):
    '''
    Компонент используемый для блокирования колонок
    '''
    def __init__(self, *args, **kwargs):
        super(ExtGridLockingView, self).__init__(*args, **kwargs)
        self.init_component(*args, **kwargs)

    def render(self):
        result = 'new Ext.ux.grid.LockingGridView()'
        return result

#===============================================================================
class ExtGridLockingHeaderGroupView(BaseExtComponent):
    '''
    Компонент используемый для блокирования колонок и их группировки
    '''
    def __init__(self, *args, **kwargs):
        super(ExtGridLockingHeaderGroupView, self).__init__(*args, **kwargs)
        self.grid = None
        self.init_component(*args, **kwargs)

    def render(self):
        result = 'new Ext.ux.grid.LockingHeaderGroupGridView({rows:%s})' % self.grid.t_render_banded_columns()
        return result
