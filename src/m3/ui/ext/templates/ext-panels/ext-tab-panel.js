new Ext.TabPanel({
	{% include 'base-ext-ui.js'%}
	
	{% if component.icon_cls %} ,iconCls: '{{ component.icon_cls }}' {% endif %}
	{% if component.title %} ,title: '{{ component.title }}' {% endif %}
    {% if component.deferred_render != None %},deferredRender: {{ component.deferred_render|lower }} {% endif %}
    ,activeTab:0
	,autoWidth: true
    {% if component.enable_tab_scroll %}
    ,enableTabScroll: true
    {% else %}
    ,enableTabScroll: false
    {% endif %}
    , border: {{component.border|lower}}
    , bodyBorder: {{component.body_border|lower}}
	,items: [{{ component.t_render_items|safe }}]
})
