/**
 * 
 */
function createTreeView(rootNodeName){
	var tree =  new Ext.tree.TreePanel({
		useArrows: true
	    ,autoScroll: true
	    ,animate: true    
	    ,containerScroll: true
	    ,border: false					        
	    ,loader: new Ext.tree.TreeLoader({
			url: '/project-files'
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
		        },{
		            id: 'rename-file'
		            ,text: 'Переименовать файл'
		            ,iconCls: 'icon-script-edit'
		        },{
		            id: 'delete-file'
		            ,text: 'Удалить файл'
		            ,iconCls: 'icon-script-delete'
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
					            		,success: function(){
					            			var new_node = new Ext.tree.TreeNode({
					            				text: text
					            				,path: attr['path']
					            				,class_name: text
					            				,iconCls: 'icon-page-white-c'	
					            				,leaf: true			            				
					            			});
	
					            			node.appendChild(new_node);
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
		    listeners: {
		        contextmenu: function(node, e) {
		            node.select();	            
		            if (node.text === 'ui.py' || node.text === 'forms.py' ) {
			            var c = node.getOwnerTree().contextMenu;
			            c.contextNode = node;
			            c.showAt(e.getXY());						            	
		            }
	
		        },
		        dblclick: function(node, e){	        	
		        	if (node.parentNode && (node.parentNode.text === 'ui.py' || node.parentNode.text === 'forms.py' ) ){
			        	onClickNode(node);
		        	}
		        }
		    }	
	})
	
	
	tree.getLoader().on("beforeload", function(treeLoader, node) {	
    	treeLoader.baseParams['path'] = node.attributes.path;
	}, this);
	
	return tree;
}

var tabPanel = new Ext.TabPanel({	
	region: 'center'
    ,xtype: 'tabpanel' 
    ,activeTab: 0
    ,items: [{
    	title: 'Обзор'
		,html: '<iframe src="http://m3.bars-open.ru" width="100%" height="100%" style="border: 0px none;"></iframe>'
    }]	    
});


function onClickNode(node) {					
	var attr =  node.attributes;	            	
	
	var starter = new Bootstrapper();
	var panel = starter.init(
				'/designer/data', 
				'/designer/save', 
				attr['path'], 
				attr['class_name']);
				   	 
   	panel.setTitle(attr['class_name']); 
	tabPanel.add( panel );
	
	starter.loadModel();
	
	tabPanel.activate(panel);
}


