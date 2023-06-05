from django import template

register = template.Library()
@register.filter
def get_index(lst, i):
    return lst[i]