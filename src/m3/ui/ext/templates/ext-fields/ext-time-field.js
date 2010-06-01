new Ext.form.TimeField({
	{% include 'base-ext-ui.js'%}
	
	{% if component.label %} ,fieldLabel: '{{ component.label }}' {% endif %}
	{% if component.name %} ,name: '{{ component.name }}' {% endif %}
	{% if component.value %} ,value: '{{ component.value }}' {% endif %}
	{% if component.label_style %} ,labelStyle: "{{ component.t_render_label_style|safe }}" {% endif %}
	{% if component.read_only %} ,readOnly: true {% endif %}
	{% if component.format %} ,format: "{{ component.format }}" {% endif %}
	{% if not component.allow_blank %} ,allowBlank: false {% endif %}
	
	{% if component.increment %} ,increment: {{ component.increment }} {% endif %}
})