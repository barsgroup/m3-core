new Ext.Container({
	layout: 'column',
	items:
		[{
			xtype: 'container',
			layout: 'form',
			items: {
				xtype: 'textfield'
				,id: "{{ component.client_id }}"
				{% if component.disabled %} ,disabled: true {% endif %}
				{% if component.hidden %} ,hidden: true {% endif %}
				{% if component.width %} ,width: {{ component.width }} {% endif %}
				{% if component.height %} ,height: {{ component.height }} {% endif %}
				{% if component.html  %} ,html: '{{ component.html|safe }}' {% endif %}
				{% if component.style %} ,style: {{ component.t_render_style|safe }} {% endif %}
				{% if component.x %} ,x: {{ component.x }} {% endif %}
				{% if component.y %} ,y: {{ component.y }} {% endif %}
				
				{% if component.label %} ,fieldLabel: '{{ component.label }}' {% endif %}
				{% if component.name %} ,name: '{{ component.name }}' {% endif %}
				{% if component.value %} ,value: '{{ component.value }}' {% endif %}
				{% if component.label_style %} ,labelStyle: "{{ component.t_render_label_style|safe }}" {% endif %}
				,readOnly: true
			}
		},
		{{ component.t_render_select_button|safe }},
		{{ component.t_render_clean_button|safe }}
	]
})
