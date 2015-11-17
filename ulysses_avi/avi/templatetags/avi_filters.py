'''
GAVIP Example AVIS: Multiple Pipeline AVI

Some custom template filters
'''

import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='addclass')
def addclass(value, arg):
    """
    Used to add css classes to ModelForm elements
    See: http://stackoverflow.com/questions/5827590/css-styling-in-django-forms
    """
    return value.as_widget(attrs={'class': arg})


@register.filter
def as_json(data):
    return mark_safe(json.dumps(data))