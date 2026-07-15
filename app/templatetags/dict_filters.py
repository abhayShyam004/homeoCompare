from django import template
from django.utils.safestring import mark_safe
import ast

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, {})

@register.filter
def as_bullet_points(value):
    """Converts a list or a string representation of a list into an HTML unordered list."""
    if not value:
        return ""
    
    items = []
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                items = parsed
            else:
                items = [value]
        except (ValueError, SyntaxError):
            items = [value]
    elif isinstance(value, list):
        items = value
    else:
        items = [str(value)]
        
    if not items:
        return ""
        
    html = "<ul style='list-style-type: disc; margin-left: 20px; padding-left: 10px;'>"
    for item in items:
        html += f"<li style='margin-bottom: 6px;'>{item}</li>"
    html += "</ul>"
    
    return mark_safe(html)
