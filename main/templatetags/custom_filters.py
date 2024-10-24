from django import template

register = template.Library()

@register.filter
def remove_all_extensions(value):
    if isinstance(value, str):
        return value.split('.')[0]
    return value

@register.filter
def format_currency(value):
    if value is None:
        return ""
    formatted_value = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{formatted_value} €"