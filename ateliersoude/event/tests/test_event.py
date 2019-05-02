import datetime

import pytest
from django.contrib.auth import get_user
from django.core import signing
from django.urls import reverse
from django.utils import timezone

from ateliersoude.event.models import Event
from ateliersoude.user.factories import USER_PASSWORD

pytestmark = pytest.mark.django_db


def _django_date(datetime):
    return str(datetime).split(".")[0]


@pytest.fixture
def event_data(
    condition_factory, activity, custom_user_factory, place, organization
):
    cond1 = condition_factory(organization=organization)
    cond2 = condition_factory(organization=organization)
    user1 = custom_user_factory()
    user2 = custom_user_factory()
    user3 = custom_user_factory()
    user4 = custom_user_factory()
    organization.volunteers.add(user1, user2, user3, user4)
    return {
        "organization": organization,
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
    response = client.get(reverse("event:detail", args=[event.pk, event.slug]))
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


def test_get_event_create(client, user_log, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    response = client.get(reverse("event:create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Création d'un nouvel évènement" in html


def test_get_event_create_403(client, organization):
    response = client.get(reverse("event:create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 403
    assert "Vous ne pouvez pas créer" in html


def test_get_event_create_403_not_in_orga(client_log, organization):
    response = client_log.get(reverse("event:create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 403
    assert "Vous ne pouvez pas créer" in html


def test_event_create(client, user_log, event_data):
    organization = event_data.pop("organization")
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    assert Event.objects.count() == 0
    response = client.post(
        reverse("event:create", args=[organization.pk]), event_data
    )
    events = Event.objects.all()
    assert response.status_code == 302
    assert len(events) == 1
    assert response["Location"] == reverse(
        "event:detail", args=[events[0].pk, events[0].slug]
    )


def test_event_create_invalid(client, user_log, event_data):
    organization = event_data.pop("organization")
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    assert Event.objects.count() == 0
    data = event_data
    del data["starts_at"]
    response = client.post(
        reverse("event:create", args=[organization.pk]), data
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert Event.objects.count() == 0
    assert "Ce champ est obligatoire." in html


def test_get_event_update(client, user_log, event_factory, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    event = event_factory()
    response = client.get(
        reverse("event:edit", args=[event.pk, organization.pk])
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert f"Mise à jour de '" in html
    assert event.activity.name in html


def test_event_update(client, user_log, event_factory, event_data):
    organization = event_data.pop("organization")
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    event = event_factory()
    event_data["available_seats"] = 10
    response = client.post(
        reverse("event:edit", args=[event.pk, organization.pk]), event_data
    )
    events = Event.objects.all()
    assert response.status_code == 302
    assert len(events) == 1
    assert events[0].available_seats == 10
    assert response["Location"] == reverse(
        "event:detail", args=[events[0].pk, events[0].slug]
    )


def test_get_event_update_403(client, organization, event):
    response = client.get(
        reverse("event:edit", args=[event.pk, organization.pk])
    )
    html = response.content.decode()
    assert response.status_code == 403
    assert "Vous ne pouvez pas créer" in html


def test_get_event_update_403_not_in_orga(client_log, organization, event):
    response = client_log.get(
        reverse("event:edit", args=[event.pk, organization.pk])
    )
    html = response.content.decode()
    assert response.status_code == 403
    assert "Vous ne pouvez pas créer" in html


def test_cancel_reservation_wrong_token(client):
    token = signing.dumps({"user_id": 1, "event_id": 2}, salt="unknown")
    resp = client.get(reverse("event:cancel_reservation", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse("event:list")


def test_cancel_reservation(client, event_factory, custom_user_factory):
    user = custom_user_factory()
    event = event_factory()
    event.registered.add(user)
    nb_registered = Event.objects.first().registered.count()
    assert nb_registered == 1
    token = signing.dumps(
        {"user_id": user.id, "event_id": event.id}, salt="cancel"
    )
    resp = client.get(reverse("event:cancel_reservation", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    nb_registered = Event.objects.first().registered.count()
    assert nb_registered == 0


def test_cancel_reservation_redirect(
    client, event_factory, custom_user_factory
):
    user = custom_user_factory()
    event = event_factory()
    event.registered.add(user)
    token = signing.dumps(
        {"user_id": user.id, "event_id": event.id}, salt="cancel"
    )
    query_params = "?redirect=/location/"
    resp = client.get(
        reverse("event:cancel_reservation", args=[token]) + query_params
    )
    assert resp.status_code == 302
    assert resp["Location"] == reverse("location:list")


def test_book_wrong_token(client):
    token = signing.dumps({"user_id": 1, "event_id": 2}, salt="unknown")
    resp = client.get(reverse("event:book", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse("event:list")


def test_book(client, event_factory, custom_user_factory):
    user = custom_user_factory()
    event = event_factory()
    nb_registered = Event.objects.first().registered.count()
    assert nb_registered == 0
    token = signing.dumps(
        {"user_id": user.id, "event_id": event.id}, salt="book"
    )
    resp = client.get(reverse("event:book", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    nb_registered = Event.objects.first().registered.count()
    assert nb_registered == 1


def test_book_redirect(client, event_factory, custom_user_factory):
    user = custom_user_factory()
    event = event_factory()
    token = signing.dumps(
        {"user_id": user.id, "event_id": event.id}, salt="book"
    )
    query_params = "?redirect=/location/"
    resp = client.get(reverse("event:book", args=[token]) + query_params)
    assert resp.status_code == 302
    assert resp["Location"] == reverse("location:list")


def test_user_present_wrong_token(client):
    token = signing.dumps({"user_id": 1, "event_id": 2}, salt="unknown")
    resp = client.get(reverse("event:user_present", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse("event:list")


def test_user_present(client, event_factory, custom_user_factory):
    user = custom_user_factory()
    event = event_factory()
    nb_presents = Event.objects.first().presents.count()
    assert nb_presents == 0
    token = signing.dumps(
        {"user_id": user.id, "event_id": event.id}, salt="present"
    )
    resp = client.get(reverse("event:user_present", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    nb_presents = Event.objects.first().presents.count()
    assert nb_presents == 1


def test_user_present_redirect(client, event_factory, custom_user_factory):
    user = custom_user_factory()
    event = event_factory()
    token = signing.dumps(
        {"user_id": user.id, "event_id": event.id}, salt="present"
    )
    query_params = "?redirect=/location/"
    resp = client.get(
        reverse("event:user_present", args=[token]) + query_params
    )
    assert resp.status_code == 302
    assert resp["Location"] == reverse("location:list")


def test_user_absent_wrong_token(client):
    token = signing.dumps({"user_id": 1, "event_id": 2}, salt="unknown")
    resp = client.get(reverse("event:user_absent", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse("event:list")


def test_user_absent(client, event_factory, custom_user_factory):
    user = custom_user_factory()
    event = event_factory()
    event.presents.add(user)
    nb_presents = Event.objects.first().presents.count()
    assert nb_presents == 1
    token = signing.dumps(
        {"user_id": user.id, "event_id": event.id}, salt="absent"
    )
    resp = client.get(reverse("event:user_absent", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    nb_presents = Event.objects.first().presents.count()
    assert nb_presents == 0


def test_user_absent_redirect(client, event_factory, custom_user_factory):
    user = custom_user_factory()
    event = event_factory()
    token = signing.dumps(
        {"user_id": user.id, "event_id": event.id}, salt="absent"
    )
    query_params = "?redirect=/location/"
    resp = client.get(
        reverse("event:user_absent", args=[token]) + query_params
    )
    assert resp.status_code == 302
    assert resp["Location"] == reverse("location:list")
