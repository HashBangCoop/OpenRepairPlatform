import datetime

import pytest
from django.contrib.auth import get_user
from django.urls import reverse
from django.utils import timezone

from ateliersoude.event.models import Event

pytestmark = pytest.mark.django_db


def _django_date(datetime):
    return str(datetime).split(".")[0]


@pytest.fixture
def event_data(
    organization_factory,
    condition_factory,
    activity_factory,
    custom_user_factory,
    place_factory,
):
    orga = organization_factory()
    cond1 = condition_factory()
    cond2 = condition_factory()
    activity = activity_factory()
    user1 = custom_user_factory()
    user2 = custom_user_factory()
    user3 = custom_user_factory()
    user4 = custom_user_factory()
    place = place_factory()
    return {
        "organization": orga.pk,
        "conditions": [cond1.pk, cond2.pk],
        "published": False,
        "publish_at": _django_date(timezone.now()),
        "activity": activity.pk,
        "starts_at": _django_date(
            timezone.now() + datetime.timedelta(hours=4)
        ),
        "ends_at": _django_date(timezone.now() + datetime.timedelta(hours=7)),
        "available_seats": 12,
        "registered": [user1.pk, user2.pk, user3.pk],
        "presents": [user1.pk, user2.pk],
        "organizers": [user4.pk],
        "location": place.pk,
    }


# TODO: more tests on `event_list` when filter is implemented


def test_event_list(client, event_factory, published_event_factory):
    response = client.get(reverse("event:list"))
    assert response.status_code == 200
    assert get_user(client).is_anonymous
    assert "Aucun évènement trouvé" in response.content.decode()
    unpublished_event = event_factory()
    event1 = published_event_factory()
    event2 = published_event_factory()
    response = client.get(reverse("event:list"))
    html = response.content.decode()
    assert unpublished_event.activity.name not in html
    assert unpublished_event.activity.description not in html
    assert event1.activity.name in html
    assert event1.activity.description in html
    assert event2.activity.name in html
    assert event2.activity.description in html


def test_event_detail_context(client, event_factory):
    event = event_factory()
    response = client.get(
        reverse("event:detail", args=[event.pk, event.slug])
    )
    assert response.status_code == 200
    assert isinstance(response.context_data["event"], Event)
    assert event.pk == response.context_data["event"].pk
    assert event.activity.name in str(response.context_data["event"])


def test_get_event_delete(client, event_factory):
    event = event_factory()
    response = client.get(reverse("event:delete", args=[event.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert event.activity.name in html
    assert event.organization.name in html


def test_event_delete(client, event_factory):
    event = event_factory()
    assert Event.objects.count() == 1
    response = client.post(reverse("event:delete", args=[event.pk]))
    assert Event.objects.count() == 0
    assert response.status_code == 302
    assert response["Location"] == reverse("event:list")


def test_get_event_create(client):
    response = client.get(reverse("event:create"))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Création d'un nouvel évènement" in html


def test_get_event_create_default_orga(client, organization_factory):
    org1 = organization_factory()
    response = client.get(
        reverse("event:create"),
        HTTP_REFERER="http://testserver{}".format(
            reverse("user:organization_detail", args=[org1.pk, org1.slug])
        ),
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert f'<option value="{org1.pk}" selected>' in html
    assert "Création d'un nouvel évènement" in html


def test_event_create(client_log, event_data):
    assert Event.objects.count() == 0
    response = client_log.post(reverse("event:create"), event_data)
    events = Event.objects.all()
    assert response.status_code == 302
    assert len(events) == 1
    assert response["Location"] == reverse(
        "event:detail", args=[events[0].pk, events[0].slug]
    )


# TODO: test create/update activity with organization where user isn't admin


def test_event_create_invalid(client, event_data):
    assert Event.objects.count() == 0
    data = event_data
    del data["organization"]
    response = client.post(reverse("event:create"), data)
    html = response.content.decode()
    assert response.status_code == 200
    assert Event.objects.count() == 0
    assert "Ce champ est obligatoire." in html


def test_get_event_update(client, event_factory):
    event = event_factory()
    response = client.get(reverse("event:edit", args=[event.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert f"Mise à jour de '" in html
    assert event.activity.name in html


def test_event_update(client_log, event_factory, event_data):
    event = event_factory()
    event_data["available_seats"] = 10
    response = client_log.post(
        reverse("event:edit", args=[event.pk]), event_data
    )
    events = Event.objects.all()
    assert response.status_code == 302
    assert len(events) == 1
    assert events[0].available_seats == 10
    assert response["Location"] == reverse(
        "event:detail", args=[events[0].pk, events[0].slug]
    )
