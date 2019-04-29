from django import template
from django.core import signing

register = template.Library()


@register.simple_tag(name="token")
def serialize_id(user, event, action):
    data = {"user_id": user.id, "event_id": event.id}
    return signing.dumps(data, salt=action)
