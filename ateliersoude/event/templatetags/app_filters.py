from django import template
from django.core import signing

register = template.Library()


@register.simple_tag
def tokenize(user, event, action):
    data = {"user_id": user.id, "event_id": event.id}
    return signing.dumps(data, salt=action)


@register.filter
def initial(form, user):
    form.initial.update(user.__dict__)
    return form


@register.simple_tag
def filter_orga(queryset, organization):
    return queryset.filter(organization=organization).first()
