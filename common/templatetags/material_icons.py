from django import template
from django.urls import reverse
from django.utils.html import mark_safe

register = template.Library()

@register.simple_tag
def material_icon_button(icon_name, class_name="", url="", text=""):
    button_html = f'''
        <button {'' if url else 'disabled'} class="btn {class_name} d-flex justify-content-center align-content-between">
            <span class="material-icons">
                {icon_name}
            </span>
            {text}
        </button>
    '''
    
    if url:
        # url_path = reverse(url)
        return mark_safe(f'<a class="link" href="{url}">{button_html}</a>')
    else:
        return mark_safe(button_html)