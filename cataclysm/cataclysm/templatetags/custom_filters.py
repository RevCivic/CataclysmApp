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

@register.filter
def ability_score_modifier(score):
    modifier = (score - 10) // 2
    return modifier

@register.filter
def get_json_value(json_object, key):
    return json_object.get(key)

@register.filter
def read_hlo_text(text):
    return text.replace('\\n', '<br>').replace("{b}","<b>").replace("{/b}","</b>").replace("{i}","<i>").replace("{/i}","</i>")