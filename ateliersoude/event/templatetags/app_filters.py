from django import template
from django.core import signing

register = template.Library()


@register.simple_tag
def tokenize(user, event, action):
    data = {"user_id": user.id, "event_id": event.id}
    return signing.dumps(data, salt=action)


@register.filter
def lookup(hashtable, target):
    return hashtable.get(target)
