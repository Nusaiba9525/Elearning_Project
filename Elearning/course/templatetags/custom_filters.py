from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retrieve item from dictionary by key."""
    print(f"Fetching {key} from dictionary")  # Debugging statement
    return dictionary.get(key)