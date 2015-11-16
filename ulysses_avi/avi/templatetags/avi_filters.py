#
# Derek O'Callaghan (Parameter Space) 2015
#

from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(value, arg):
    """
    Used to add css classes to ModelForm elements
    See: http://stackoverflow.com/questions/5827590/css-styling-in-django-forms
    """
    return value.as_widget(attrs={'class': arg})
