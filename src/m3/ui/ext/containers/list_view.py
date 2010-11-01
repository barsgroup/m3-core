#coding:utf-8
'''
Created on 31.03.2010

@author: prefer
'''

from base import BaseExtPanel
from m3.ui.ext.containers import (ExtGridColumn, 
                              ExtGridBooleanColumn, 
                              ExtGridDateColumn, 
                              ExtGridNumberColumn)

#===============================================================================
class ExtListView(BaseExtPanel):
    '''
    Класс list view в соответствии с Ext.list.ListView
    
    @version: 0.1
    @begin_designer
    {title: "List view"
    ,ext_class: "Ext.ListView"
    ,xtype: "listview"
    ,attr: [{
        ext_attr: "multiSelect"
        ,py_attr: "multi_select" 
    },{
        ext_attr: "emptyText"
        ,py_attr: "empty_text"
    },{
        ext_attr: "columns"
        ,py_attr: "columns"
    }]}
    @end_designer
    '''
    def __init__(self, *args, **kwargs):
        super(ExtListView, self).__init__(*args, **kwargs)
        self.template = 'ext-containers/ext-list-view.js'
        self.multi_select = False
        self.empty_text = None
        self.__store = None
        self._items = []
        self.init_component(*args, **kwargs)
        
    def set_store(self, store):
        self.__store = store
        
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
        
    @property
    def columns(self):
        return self._items