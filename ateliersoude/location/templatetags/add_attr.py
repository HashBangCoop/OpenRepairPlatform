from django import template
register = template.Library()


@register.filter(name='add_class')
def add_class(field, classes):
    existing_class = field.field.widget.attrs.get("class", "")
    field.field.widget.attrs["class"] = f"{existing_class} {classes}"
    return field
