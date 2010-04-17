#coding:utf-8
'''
Created on 11.3.2010

@author: prefer
'''

from base import BaseExtPanel
from m3.ui.ext.base import ExtUIComponent, BaseExtComponent
from m3.ui.ext.containers import ExtGridColumn, ExtGridBooleanColumn, ExtGridDateColumn, ExtGridNumberColumn

from m3.helpers.datastructures import TypedList


class ExtTree(BaseExtPanel):
    def __init__(self, *args, **kwargs):
        super(ExtTree, self).__init__(*args, **kwargs)
        self.template = 'ext-trees/ext-tree.js'
        self.nodes = TypedList(type=ExtTreeNode)
        self._items = []
        self.tree_loader = ExtTreeLoader()
        self.url = None
        self.init_component(*args, **kwargs)
    
    @staticmethod    
    def nodes_auto_check(node):
        node.auto_check = True
        for child in node.children:
            ExtTree.nodes_auto_check(child)         
    
    def t_render_tree_loader(self):
        if not self.tree_loader.url:
            # Проставим у всех узлов автопроверку
            for node in self.nodes:
                ExtTree.nodes_auto_check(node)
        return self.tree_loader.render()
    
    def t_render_nodes(self):
        return ','.join([node.render() for node in self.nodes])
    
    def t_render_columns(self):
        return self.t_render_items()
    
    def add_nodes(self, *args):
        for node in args:
            self.nodes.append(node)
    
    def add_column(self,**kwargs):
        self.columns.append(ExtGridColumn(**kwargs))
        
    def add_bool_column(self,**kwargs):
        self.columns.append(ExtGridBooleanColumn(**kwargs))
        
    def add_number_column(self,**kwargs):
        self.columns.append(ExtGridNumberColumn(**kwargs))
        
    def add_date_column(self,**kwargs):
        self.columns.append(ExtGridDateColumn(**kwargs))
        
    @property
    def columns(self):
        return self._items
    
    @property
    def url(self):
        return self.__url
    
    @url.setter
    def url(self, value):
        self.tree_loader.url = value
        self.__url = value
   
    #//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\
    # Врапперы над событиями listeners[...]
    #------------------------------------------------------------------------
    @property
    def handler_contextmenu(self):
        return self._listeners.get('contextmenu')
    
    @handler_contextmenu.setter
    def handler_contextmenu(self, menu):
        menu.container = self
        self._listeners['contextmenu'] = menu
    
    @property
    def handler_containercontextmenu(self):
        return self._listeners.get('containercontextmenu')
    
    @handler_containercontextmenu.setter
    def handler_containercontextmenu(self, menu):
        menu.container = self
        self._listeners['containercontextmenu'] = menu
        
    @property
    def handler_click(self):
        return self._listeners.get('click')
    
    @handler_click.setter
    def handler_click(self, function):
        self._listeners['click'] = function
    #------------------------------------------------------------------------
    
    
class ExtTreeNode(ExtUIComponent):
    def __init__(self,*args, **kwargs):
        super(ExtTreeNode, self).__init__(*args, **kwargs)
        self.template = 'ext-trees/ext-tree-node.js'
        self.text = None
        self.leaf = False
        self.has_children = False
        #self.node_id = '' # используется client_id
        self.expanded = False
        self.auto_check = False
        self.children = TypedList(type=ExtTreeNode)
        self.__items = {}
        self.init_component(*args, **kwargs)
                 
    def t_render_children(self):
        return '[%s]' % ','.join([child.render() for child in self.children])
             
    def add_children(self, children):
        '''
            Добавляет дочерние узлы
            Если необходимо, здесь можно указать у узлов атрибут "parent" на текущий (родительский) узел
        '''
        self.has_children = True
        self.children.append(children)
       
    @property    
    def items(self):
        return self.__items
    
    def set_items(self, **kwargs):
        for k, v in kwargs.items():
            self.items[k] = v
        
        
class ExtTreeLoader(BaseExtComponent):
    def __init__(self, *args, **kwargs):
        super(ExtTreeLoader, self).__init__(*args, **kwargs)
        self.template = 'ext-trees/ext-tree-loader.js'
        self.url = None
        self.init_component(*args, **kwargs)
