from django import template
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

register = template.Library()

@register.filter(name='highlight')
def highlight_code(value, lang):
    lexer = get_lexer_by_name(lang, stripall=True)
    formatter = HtmlFormatter(nowrap=True)
    return mark_safe(highlight(value, lexer, formatter))
