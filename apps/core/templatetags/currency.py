# apps/core/templatetags/currency.py
from django import template

register = template.Library()

@register.filter
def naira(kobo):
    return f"{kobo / 100:,.2f}"
