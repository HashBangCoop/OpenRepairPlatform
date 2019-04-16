from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now

from ateliersoude.plateformeweb.models import (
    Event,
    OrganizationPerson,
    PublishedEvent,
)

# See https://stackoverflow.com/a/28533875

# NOTE requiert plateformeweb.context_processors.user_data dans les context
# processors de settings.py

# rajoute 2 variables de template dans le contexte
# - my_events_attending (events futurs ou le user participe,
# publiés uniquement)
# - my_events_organizing (tous les events futurs où le user organise, publiés
#   ou non)


def user_data(request):
    if isinstance(request.user, AnonymousUser) or request.user is None:
        return {}
    events_attending = PublishedEvent.objects.all().filter(
        attendees=request.user, ends_at__gte=now()
    )
    last_event_attending = (
        PublishedEvent.objects.all()
        .filter(attendees=request.user, ends_at__gte=now())
        .order_by("starts_at")[:1]
    )
    events_organizing = Event.objects.all().filter(
        organizers=request.user, ends_at__gte=now()
    )
    return {
        "my_events_attending": events_attending,
        "my_last_event_attending": last_event_attending,
        "my_events_organizing": events_organizing,
    }


def last_events(request):
    events = (
        PublishedEvent.objects.all()
        .filter(starts_at__gte=now())
        .order_by("starts_at")[:4]
    )
    return {"last_events": events}


def user_in_organization(request):
    users = OrganizationPerson.objects.all()
    return {"user_in_organization": users}


def admin_of_organizations(request):
    if request.user.is_authenticated:
        orgs = OrganizationPerson.objects.filter(
            user=request.user, role__gte=OrganizationPerson.ADMIN
        )
        if orgs:
            return {"admin_of_organizations": True}
    return {"admin_of_organizations": False}
