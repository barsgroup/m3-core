/**
 * Адаптер
 * @param fn - Функция
 */
function toolBarFuncWraper(fn){
    var cmp = Ext.getCmp('project-view');
    var selectedNode = cmp.getSelectionModel().getSelectedNode();
    if (selectedNode){
        fn(selectedNode);
    }
    else{
        Ext.Msg.show({
        title: 'Информация',
        msg: 'Для выполнения действия необходимо выделить узел дерева',
        buttons: Ext.Msg.OK,
        icon: Ext.Msg.INFO
    });
    };
};
/**
 * 
 */
function createTreeView(rootNodeName){
	var tree =  new Ext.tree.TreePanel({
		useArrows: true
		,id:'project-view'
	    ,autoScroll: true
	    ,animate: true    
	    ,containerScroll: true
	    ,border: false
	    ,header: false		        
	    ,loader: new Ext.tree.TreeLoader({
			url: '/project-files'
		})
		,tbar: new Ext.Toolbar({			
            items: [{
            	iconCls: 'icon-script-add',
            	tooltip:'Создать файл',
                handler: function(item, e){toolBarFuncWraper(newFile)}
            },{
            	iconCls: 'icon-script-edit',
            	tooltip:'Переименовать файл',
                handler: function(item, e){toolBarFuncWraper(renameFile)}
            },{
            	iconCls: 'icon-script-delete',
            	tooltip:'Удалить файл',
                handler: function(item, e){toolBarFuncWraper(deleteFile)}
            },{
                tooltip: 'Редактировать файл',
		        iconCls: 'icon-script-lightning',
                handler: function(item, e){toolBarFuncWraper(editFile)}
            },{
            	xtype: 'tbseparator'
            },{
            	iconCls: 'icon-arrow-refresh'
            	,tooltip:'Обновить структуру проекта'
            	,handler: function(){
            		var cmp = Ext.getCmp('project-view');
					var loader = cmp.getLoader();
		        	var rootNode = cmp.getRootNode();
		        	loader.load(rootNode);
		        	rootNode.expand();
            	}
            }]        
		})
	    ,root: {
	        nodeType: 'async'
	        ,text: rootNodeName
	        ,draggable: false
	        ,id: 'source'
	        ,expanded: true					     
	    }
		,contextMenu: new Ext.menu.Menu({
                items: [{
		            id: 'create-file'
		            ,text: 'Создать файл'
		            ,iconCls: 'icon-script-add'
                    ,handler: function(item, e){newFile(item.parentMenu.contextNode, e)}
		        },{
		            id: 'rename-file'
		            ,text: 'Переименовать файл'
		            ,iconCls: 'icon-script-edit'
                    ,handler: function(item, e){renameFile(item.parentMenu.contextNode, e)}
		        },{
		            id: 'delete-file'
		            ,text: 'Удалить файл'
		            ,iconCls: 'icon-script-delete'
                    ,handler: function(item, e){deleteFile(item.parentMenu.contextNode,e)}
		        },{
		            id: 'edit-file'
		            ,text: 'Редактировать файл'
		            ,iconCls: 'icon-script-lightning'
                    ,handler: function(item, e){editFile(item.parentMenu.contextNode,e)}
		        },'-',{
		        	id: 'create-class'
		            ,text: 'Добавить класс'
		            ,iconCls: 'icon-cog-add'
		            ,handler: function(item, e){

						Ext.MessageBox.prompt('Создание класса',
							'Введите название класса',
							function(btn, text){
								if (btn == 'ok'){
									var node = item.parentMenu.contextNode;
						            var attr = node.attributes;
					            	Ext.Ajax.request({
					            		url:'/create-new-class'
					            		,params: {
					            			path: attr['path']
					            			,className: text
					            		}
					            		,success: function(response, opts){
					            			var obj = Ext.util.JSON.decode(response.responseText);
					            			if (obj.success) {
						            			var new_node = new Ext.tree.TreeNode({
						            				text: text
						            				,path: attr['path']
						            				,class_name: text
						            				,iconCls: 'icon-class'
						            				,leaf: true
						            			});

						            			node.appendChild(new_node);
								           	} else {
								           		Ext.Msg.show({
												   title:'Ошибка'
												   ,msg: obj.json
												   ,buttons: Ext.Msg.OK
												   ,icon: Ext.MessageBox.WARNING
												});
								           	}

					            		},
					            		failure: uiAjaxFailMessage
					            	});
					            }
							}
						);
		            }
		        }
		        ]
		    }),
            contextFileMenu: new Ext.menu.Menu({
                items: [{
		            id: 'create-file2'
		            ,text: 'Создать файл'
		            ,iconCls: 'icon-script-add'
                    ,handler: function(item, e){newFile(item.parentMenu.contextNode, e)}
		        },{
		            id: 'rename-file2'
		            ,text: 'Переименовать файл'
		            ,iconCls: 'icon-script-edit'
                    ,handler: function(item, e){renameFile(item.parentMenu.contextNode, e)}
		        },{
		            id: 'delete-file2'
		            ,text: 'Удалить файл'
		            ,iconCls: 'icon-script-delete'
                    ,handler: function(item, e){deleteFile(item.parentMenu.contextNode,e)}
		        },{
		            id: 'edit-file1'
		            ,text: 'Редактировать файл'
		            ,iconCls: 'icon-script-lightning'
                    ,handler: function(item, e){editFile(item.parentMenu.contextNode,e)}
		        }]
            }),
            contextDirMenu: new Ext.menu.Menu({
                items: [{
		            id: 'create-dir'
		            ,text: 'Создать директорию'
		            ,iconCls: 'icon-folder-add'
                    ,handler: function(item, e){}
		        },{
		            id: 'rename-dir'
		            ,text: 'Переименовать директорию'
		            ,iconCls: 'icon-folder-edit'
                    ,handler: function(item, e){}
		        },{
		            id: 'delete-dir'
		            ,text: 'Удалить директорию'
		            ,iconCls: 'icon-folder-delete'
                    ,handler: function(item, e){}
		        },'-',{
		            id: 'create-file3'
		            ,text: 'Создать файл'
		            ,iconCls: 'icon-script-add'
                    ,handler: function(item, e){newFile(item.parentMenu.contextNode, e)}
                }]
            }),
		    listeners: {
		        contextmenu: function(node, e) {
		            node.select();
                    var parentNodeText = node.parentNode.text;
                    /* Файл дизайна форм */
		            if (node.text === 'ui.py' || node.text === 'forms.py' ) {
			            var c = node.getOwnerTree().contextMenu;
			            c.contextNode = node;
			            c.showAt(e.getXY());						            	
		            }
                    /* Файл */
                    else if(node.leaf && (parentNodeText !== 'ui.py' && parentNodeText !== 'forms.py')) {
                        var c = node.getOwnerTree().contextFileMenu;
			            c.contextNode = node;
			            c.showAt(e.getXY());
                    }
                    /* Директория */
                    else if(!node.leaf && (parentNodeText !== 'ui.py' && parentNodeText !== 'forms.py')) {
                        var c = node.getOwnerTree().contextDirMenu;
			            c.contextNode = node;
			            c.showAt(e.getXY());
                    };
		        },
		        dblclick: function(node, e){
                    var parentNodeText = node.parentNode.text;
                    var fileType = node.text.split('.').slice(-1);
		        	if (node.parentNode && (parentNodeText === 'ui.py' || parentNodeText === 'forms.py' ) ){
			        	onClickNode(node);
		        	}
                    /*Все файлы не являющиеся *.py и conf */
                    else if(fileType == 'py' || fileType == 'conf'){
                        var fileAttr = {};
                        fileAttr['path'] = node.attributes.path;
                        fileAttr['fileName'] = node.attributes.text;
                        onClickNodePyFiles(node, fileAttr);
                    }
                    else if(node.leaf) wrongFileTypeMessage(fileType);
		        }
		    }
	});
	
	tree.getLoader().on("beforeload", function(treeLoader, node) {	
    	treeLoader.baseParams['path'] = node.attributes.path;
	}, this);
	
	var accordion = new Ext.Panel({
		id:'accordition-view',		   
	    layout:'accordion',	    
	    layoutConfig: {
	        animate: true,
	        collapseFirst: true	        
	    },
	    items: [{
	        title: 'Структура проекта',	 
	        layout: 'fit',       
	        items: [tree]
	    },{
	        title: 'Свойства',
	        id: 'property-panel',
	        layout: 'fit'
	    }]
	});
	return accordion;
};

/* Переменные манипуляций с Файловой Сиситемы */
/* Можно сделать в виде объекта */
var typeFile = 'file';
var typeDir = 'dir';
var actionDelete = 'delete';
var actionRename = 'rename';
var actionNew = 'new';

/* Редактировать файл */
function editFile(node, e){
    var fileType = node.text.split('.').slice(-1);
    if(fileType == 'py' || fileType == 'conf'){
        var fileAttr = {};
        fileAttr['path'] = node.attributes.path;
        fileAttr['fileName'] = node.attributes.text;
        onClickNodePyFiles(node, fileAttr);
    }
    else wrongFileTypeMessage(fileType);
};

/* Новый файл */
function newFile(node, e){
    Ext.MessageBox.prompt('Ноый файл','Введите имя файла',
    function(btn, name){
        if (btn == 'ok' && name){
            var path = node.attributes['path'];
            var params = {
                path : path,
                type: typeFile,
                name : name,
                action : actionNew
            };
            manipulationRequest(params, function(obj){
                var new_node = new Ext.tree.TreeNode({
                    text: name
                    ,path: obj.data['path']
                    ,iconCls: 'icon-page-white-py'
                    ,leaf: true
                });
                node.appendChild(new_node);
                node.parentNode.reload();
            });
        };
    }
);
};
/* Удалить файл */
function deleteFile(node, e){
    var path = node.attributes['path'];
    var params = {
        path : path,
        type: typeFile,
        action : actionDelete
    };
    Ext.Msg.show({
        title:'Удалить файл',
        msg: 'Вы действительно хотите удалить файл?',
        buttons: Ext.Msg.YESNOCANCEL,
        icon: Ext.MessageBox.QUESTION,
        fn: function(btn, text){
            if (btn == 'yes'){
                params.access = 1;
                manipulationRequest(params, function(){
                    node.remove();
                });
            };
        }
    });
};

/* Преименовать файл */
function renameFile(node, e){
    Ext.MessageBox.prompt('Переименование файла','Введите имя файла',
    function(btn, name){
        if (btn == 'ok' && name){
        var path = node.attributes['path'];
        var params = {
            path : path,
            type: typeFile,
            action : actionRename,
            name : name
        };
        manipulationRequest(params, function(){
            node.setText(name);
            node.parentNode.reload();
        });
        };
    });
};

/* Новая директория */
/* Удалить директорию */
/* Преименовать директорию */

/**
 * DRY
 * @param params - Параметры запроса
 * @param fn - Функция которая будет выполнена при success
 */
function manipulationRequest(params, fn){
    var errorTypeExist = 'exist';
    Ext.Ajax.request({
        url:'/designer/project-manipulation',
        method: 'GET',
        params: params,
        success: function(response, opts){
            var obj = Ext.util.JSON.decode(response.responseText);
            if (obj.success && fn instanceof Function) fn(obj);
            else if (obj.error.msg && obj.error.type == errorTypeExist){
                var additionalMessage = '. Зменить?';
                customMessage(obj, params, fn,additionalMessage)
            }
            else if (obj.error.msg){
                Ext.Msg.show({
                   title:'Ошибка',
                   msg: obj.error.msg,
                   buttons: Ext.Msg.OK,
                   icon: Ext.MessageBox.WARNING
                   });
            };
        },
        failure: uiAjaxFailMessage
    });
};

/**
 *
 * @param obj - Объект ответа сервера
 * @param params - Параметры запроса к серверу, для послед. запроса
 * @param fn - Функция которая передается в рекурсивно вызывающийся запрос
 * @param additionalMessage - добавочное сообщение
 */
function customMessage(obj, params, fn, additionalMessage){
    Ext.Msg.show({
        title:'Уведомление',
        msg: obj.error.msg + additionalMessage,
        buttons: Ext.Msg.YESNOCANCEL,
        icon: Ext.MessageBox.QUESTION,
        fn: function(btn, text){
            if (btn == 'yes'){
                params.access = 1;
                manipulationRequest(params, fn);
            }
        }
    });
};

/**
 * Сообщение о неверности формата
 * @param fileType - Тип файла (*.html, *.css, ...)
 */
function wrongFileTypeMessage(fileType){
    Ext.Msg.show({
            title: 'Открытие файла',
            msg: 'Данный формат '+fileType+' не поддерживается',
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.INFO
    });
};

//Инициируем перехват нажатия ctrl+s для автоматического сохранения на сервер
Ext.fly(document).on('keydown',function(e,t,o){
   if (e.ctrlKey && (e.keyCode == 83)) {// кнопка S
   	   var tabPanel = Ext.getCmp('tab-panel');
       var tab = tabPanel.getActiveTab();
       if (tab && tab.saveOnServer &&
               (typeof(tab.saveOnServer) == 'function')) {
           tab.saveOnServer();
           e.stopEvent();
       }
   }
});

function onClickNode(node) {					
	var attr =  node.attributes;	            	

    var workspace = new DesignerWorkspace({
        dataUrl:'/designer/data',
        saveUrl:'/designer/save',
        path:attr['path'],
        className:attr['class_name'],
        previewUrl:'/designer/preview'
    });
    
 	workspace.loadModel();

    //workspace.storage.un('load', workspace.onSuccessLoad);
	workspace.on('beforeload', function(jsonObj){

		if (jsonObj['not_autogenerated']) {

       		// Может быть сгенерировать эту функцию в этом классе?
       		Ext.Msg.show({
			   title:'Функция не определена'
			   ,msg: 'Функция автогенерация не определена в классе ' + attr['class_name'] + '. <br/> Сгенерировать данную функцию?'
			   ,buttons: Ext.Msg.YESNO					   						   
			   ,icon: Ext.MessageBox.QUESTION
			   ,fn: function(btn, text){
			   		if (btn == 'yes'){
			   			generateInitialize(node, attr['path'], attr['class_name']);
			   		}			   		
			   }
			});
       		result = false;
       } else if (jsonObj.success) { 

           	var tabPanel = Ext.getCmp('tab-panel');

			this.setTitle(attr['class_name']); 
									
			tabPanel.add(this);				
		    tabPanel.activate(this);
		
		    // Прослушивает событие "tabchange", вызывает новое событие в дочерней панели
		     tabPanel.on('tabchange', function(panel,newTab,currentTab){
		         this.application.designPanel.fireEvent('tabchanged');
	    	 }, this);
	    	
       		result = true;
       	} else {
       		Ext.Msg.show({
			   title:'Ошибка'
			   ,msg: jsonObj.json
			   ,buttons: Ext.Msg.OK						   						   
			   ,icon: Ext.MessageBox.WARNING
			});
			result = false;
       	}  
       	
       return result;               	
     }, workspace);
}


/**
 * Генерирует функцию автогенерации для класса 
 */
function generateInitialize(node, path, className){
	Ext.Ajax.request({
		url:'create-autogen-function'
		,params:{
			path: path,
			className: className
		}
		,success: function(response, opts){			
			onClickNode(node);
		}
		,failure: uiAjaxFailMessage
	});
}

/**
 * Вымогает у сервера некий файл
 * @param path - путь к файлу
 * TODO: Сделать callBack'ами Ext.Ajax.request
 */
function onClickNodePyFiles(node, fileAttr){
    var path = fileAttr.path;
    var fileName = fileAttr.fileName;
    /*Запрос содержимого файла по path на сервере*/
    Ext.Ajax.request({
        url:'/file-content',
        method: 'GET',
        params: {
            path: path
        }
        ,success: function(response, opts){
            var obj = Ext.util.JSON.decode(response.responseText);
            var codeEditor = new M3Designer.code.ExtendedCodeEditor({
                sourceCode : obj.data.content
            });

            codeEditor.setTitle(fileName);
            var tabPanel = Ext.getCmp('tab-panel');
            tabPanel.add( codeEditor );
            tabPanel.activate(codeEditor);
        
            initCodeEditorHandlers(codeEditor, path);
        },
        failure: uiAjaxFailMessage
    });
};
/**
 * Иницализация хендлеров codeEditor'а
 * @param codeEditor
 */
function initCodeEditorHandlers(codeEditor, path){
    /* findByType вернет список элементов, т.к у нас всего один
    textarea забираем его по индексу */
    var textArea = codeEditor.findByType('textarea')[0];

    /* async close tab && message */
    var userTakeChoice = true;

    /* Хендлер на событие перед закрытием */
    codeEditor.on('beforeclose', function(){
        if (codeEditor.contentChanged){
            var scope = this;
            this.showMessage(function(buttonId){
                if (buttonId=='yes') {
                   scope.onSave();
                   scope.fireEvent('close_tab', scope);
                }
                else if (buttonId=='no') {
                   scope.fireEvent('close_tab', scope);
                }
                else if (buttonId=='cancel') {
                    userTakeChoice = !userTakeChoice;
                }
                userTakeChoice = !userTakeChoice;
            }, textArea.id);
        }
        else userTakeChoice = !userTakeChoice;
        return !userTakeChoice;
    });

    /* Хендлер на событие закрытие таба таб панели */
    codeEditor.on('close_tab', function(tab){
        if (tab) tabPanel.remove(tab);
    });

    /* Хендлер на событие сохранения */
    codeEditor.on('save', function(){
        /*Запрос на сохранения изменений */
        Ext.Ajax.request({
            url:'/file-content/save',
            params: {
                path: path,
                content: codeEditor.codeMirrorEditor.getCode()
            },
            success: function(response, opts){
                var obj = Ext.util.JSON.decode(response.responseText);
                var title = 'Сохранение';
                var message ='';
                var icon = Ext.Msg.INFO;
                if (obj.success)
                    message = 'Изменения были успешно сохранены';
                else if (!obj.success && obj.error){
                    message = 'Ошибка при сохранении файла\n'+obj.error;
                    icon = Ext.MessageBox.WARNING;
                };
                 Ext.Msg.show({
                    title: title,
                    msg: message,
                    buttons: Ext.Msg.OK,
                    animEl: codeEditor.id,
                    icon: icon
                 });
                codeEditor.contentChanged = false;
                codeEditor.onChange();
            },
            failure: uiAjaxFailMessage
        });
    });

    /* Хендлер на событие обновление */
    codeEditor.on('update', function(){
        var scope = this;
        /*Запрос на обновление */
        Ext.Ajax.request({
            url:'/file-content',
            method: 'GET',
            params: {
                path: path
            },
            success: function(response, opts){
                var obj = Ext.util.JSON.decode(response.responseText);
                if (codeEditor.contentChanged){
                    var msg = 'Хотели бы вы сохранить ваши изменения?';
                    codeEditor.showMessage(function(buttonId){
                        if (buttonId=='yes') {
                           scope.onSave(function(){
                               codeEditor.codeMirrorEditor.setCode(obj.data.content);
                               codeEditor.contentChanged = false;
                           });
                        }
                        else if (buttonId=='no') {
                           codeEditor.codeMirrorEditor.setCode(obj.data.content, function(){
                               codeEditor.contentChanged = false;
                           });
                        }
                        else if (buttonId=='cancel') {
                            userTakeChoice = !userTakeChoice;
                        }
                        userTakeChoice = !userTakeChoice;
                    }, textArea.id, msg);
                    codeEditor.onChange();
                }
                else userTakeChoice = !userTakeChoice;
                return !userTakeChoice;
            },
            failure: uiAjaxFailMessage
        });
    });
};
