# custom_filters.py

from django import template

register = template.Library()

@register.filter(name='add_class_and_placeholder')
def add_class_and_placeholder(field, css_class_and_placeholder):
    css_class, placeholder = css_class_and_placeholder.split(',')
    return field.as_widget(attrs={'class': css_class, 'placeholder': placeholder})


from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])
