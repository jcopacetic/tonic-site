# cms/templatetags/nav_tags.py
from django import template
from tonictail.cms.models import NavMenu

register = template.Library()

@register.simple_tag
def get_nav(name):
    try:
        nav = NavMenu.objects.get(name=name)
        print(vars(nav))
        return nav
    except NavMenu.DoesNotExist:
        return None