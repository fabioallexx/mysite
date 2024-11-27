from django import template

register = template.Library()

@register.filter
def remove_all_extensions(value):
    if isinstance(value, str):
        return value.split('.')[0]
    return value

@register.filter
def format_currency(value):
    if value is None or value == "":
        return "Valor não disponível"
    try:
        float_value = float(value)
        formatted_value = f"{float_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted_value} €"
    except (ValueError, TypeError):
        return f"Erro ao formatar: {value}"
    
@register.filter(name='get_item')
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))
    return None