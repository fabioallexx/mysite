from django import template
from django.utils.timezone import now

register = template.Library()

@register.simple_tag
def saudacao_e_hora(user):
    current_time = now()
    hour = current_time.hour
    if 5 <= hour < 12:
        greeting = "Bom dia"
    elif 12 <= hour < 18:
        greeting = "Boa tarde"
    else:
        greeting = "Boa noite"
    nome = user.username

    return f"{greeting}, {nome}! Agora são {current_time.strftime('%H:%M')}"