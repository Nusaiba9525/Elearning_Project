from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    # Add the specified CSS class to the form field widget's attributes
    return field.as_widget(attrs={"class": css_class})