from django import template

register = template.Library()

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


@register.filter(name='has_field')
def has_field(form, field_name):
    """Return True if a form contains a bound field with the given name."""
    try:
        return field_name in form.fields
    except AttributeError:
        return False