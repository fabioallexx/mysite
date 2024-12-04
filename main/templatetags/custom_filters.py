from django import template
from django.template.defaultfilters import stringfilter
import json

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

@register.filter
def remover(value):
    if isinstance(value, str):
        return value.replace('{', '').replace('}', '').replace('"', '')
    return value

@register.filter
def formatar_valores(dados):
    if isinstance(dados, str):
        try:
            pares = dados.split(",")
            resultados = []
            
            for par in pares:
                ano, valor = par.split(":")
                valor_float = float(valor.strip())
                
                if valor_float > 0:
                    valor_formatado = f"{valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    resultados.append(f"{ano.strip()}: {valor_formatado} €")
            
            return ", ".join(resultados) if resultados else "Nenhum valor disponível"
        
        except (ValueError, IndexError):
            return dados
    return dados

@register.filter
def formatar_anos(dados):
    if isinstance(dados, str):
        try:
            pares = dados.split(",")
            anos = []
            
            for par in pares:
                ano, valor = par.split(":")
                anos.append(ano.strip())
            
            return ", ".join(anos) if anos else "Nenhum valor disponível"
        
        except (ValueError, IndexError):
            return dados
    return dados

@register.filter
def get_item2(dictionary, key):
    if isinstance(dictionary, str):
        try:
            dictionary = json.loads(dictionary)
        except (json.JSONDecodeError, TypeError):
            return ''
    
    return dictionary.get(key, '')

@register.filter
def get_item3(dictionary, key):
    return dictionary.get(str(key), '')

@register.filter
def jsonify(value):
    try:
        if isinstance(value, str):
            return value
    
        if value is None:
            return '{}'
        
        return json.dumps(value)
    except Exception:
        return '{}'