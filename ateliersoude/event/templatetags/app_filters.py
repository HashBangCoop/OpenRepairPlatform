from django import template
from django.core import signing

register = template.Library()


@register.filter(name="serialize_id")
def serialize_id(user_id, event_id):
    data = {"user_id": user_id, "event_id": event_id}
    return signing.dumps(data)
