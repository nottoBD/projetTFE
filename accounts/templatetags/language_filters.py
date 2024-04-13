from django import template

register = template.Library()


@register.filter(name='compare_codes')
def prepare_code_for_comparison(language_code):
    # Fix confusion Néerlandais / Dutch
    return language_code.split('_')[0].split('-')[0]


