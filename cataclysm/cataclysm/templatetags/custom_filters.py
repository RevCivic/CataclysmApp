from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Return the current query string with the given parameters replaced/added."""
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()

@register.filter(name='isnumeric')
def isnumeric(value):
    if str(value)[0] == '-':
        return str(value).replace('-', '').isnumeric()
    return str(value).isnumeric()

@register.filter(name='isboolean')
def isboolean(value):
    return isinstance(value, bool)

@register.filter(name='sort_by_key')
def sort_by_key(value, key):
    return sorted(value, key=lambda x: x[key])