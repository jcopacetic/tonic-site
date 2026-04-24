# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Splits a string by the given separator."""
    return value.split(arg)


@register.filter
def get_tags(posts):
    """Return a deduplicated list of tags across a queryset of pages."""
    seen = set()
    tags = []
    for post in posts:
        for tag in post.tags.all():  # .all() on a prefetched relation hits cache, not DB
            if tag.slug not in seen:
                seen.add(tag.slug)
                tags.append(tag)
    return tags