new Ext.FormPanel({
    title: '{{ component.title }}',
    layout: '{{ component.layout }}',
    baseCls: 'x-plain',
    {% if component.title %} 
    header: true,
    {% else %}
    header: false,
    {% endif %}
    items: [{{ component.t_render_items|safe }}]
})