from django import template

register = template.Library()

@register.filter
def remove_all_extensions(value):
    if isinstance(value, str):
        return value.split('.')[0]
    return value