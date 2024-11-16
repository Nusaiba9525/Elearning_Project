from django import template
from quizzes.forms import ChoiceFormSet

register = template.Library()

@register.filter
def get_choice_formset(choice_formsets, index):
    return choice_formsets[index] if index < len(choice_formsets) else None