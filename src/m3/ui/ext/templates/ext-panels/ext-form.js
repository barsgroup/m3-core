new Ext.FormPanel({
	id: '{{ component.client_id }}'
	{% if component.disabled %} ,disabled: true {% endif %}
	{% if component.hidden %} ,hidden: true {% endif %}
	{% if component.width %} ,width: {{ component.width }} {% endif %}
	{% if component.height %} ,height: {{ component.height }} {% endif %}
	{% if component.html  %} ,html: '{{ component.html|safe }}' {% endif %}
	{% if component.style %} ,style: {{ component.t_render_style|safe }} {% endif %}
	{% if component.x %} ,x: {{ component.x }} {% endif %}
	{% if component.y %} ,y: {{ component.y }} {% endif %}
	
	{% if component.layout %} ,layout: '{{ component.layout }}' {% endif %}
	
	{% if component.icon_cls %} ,iconCls: '{{ component.icon_cls }}' {% endif %}
	{% if component.title %} 
		,title: '{{ component.title }}' 
		,header: true
	{% else %}
		,header: false
	{% endif %}
 	,baseCls: 'x-plain'
	{% if component.label_width  %} ,labelWidth: {{ component.label_width }} {% endif %}
	{% if component.label_align  %} ,labelAlign: '{{ component.label_align }}' {% endif %}
	{% if component.label_pad  %} ,labelPad: {{ component.label_pad }} {% endif %}
    ,items: [{{ component.t_render_items|safe }}]
})