import pytest
from django.contrib.auth import get_user
from django.urls import reverse

from ateliersoude.event.models import Activity

pytestmark = pytest.mark.django_db


@pytest.fixture
def activity_data(organization_factory):
    orga = organization_factory()
    return {
        "name": "activity_name",
        "organization": orga.pk,
        "description": "Lorem ipsum",
    }


def test_activity_list(client, activity_factory):
    response = client.get(reverse("event:activity_list"))
    assert response.status_code == 200
    assert get_user(client).is_anonymous
    assert "Aucune activité trouvée" in response.content.decode()
    activity = activity_factory()
    response = client.get(reverse("event:activity_list"))
    assert activity.name in response.content.decode()
    assert activity.description in response.content.decode()


def test_activity_detail_context(client, activity_factory):
    activity = activity_factory()
    response = client.get(
        reverse("event:activity_detail", args=[activity.pk, activity.slug])
    )
    assert response.status_code == 200
    assert isinstance(response.context_data["activity"], Activity)
    assert activity.pk == response.context_data["activity"].pk
    assert activity.name == str(response.context_data["activity"])


def test_get_activity_delete(client, activity_factory):
    activity = activity_factory()
    response = client.get(reverse("event:activity_delete", args=[activity.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert activity.name in html
    assert activity.organization.name in html


def test_activity_delete(client, activity_factory):
    activity = activity_factory()
    assert Activity.objects.count() == 1
    response = client.post(
        reverse("event:activity_delete", args=[activity.pk])
    )
    assert Activity.objects.count() == 0
    assert response.status_code == 302
    assert response["Location"] == reverse("event:activity_list")


def test_get_activity_create(client):
    response = client.get(reverse("event:activity_create"))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Création d'une nouvelle activité" in html


def test_activity_create(client_log, activity_data):
    assert Activity.objects.count() == 0
    response = client_log.post(reverse("event:activity_create"), activity_data)
    activities = Activity.objects.all()
    assert response.status_code == 302
    assert len(activities) == 1
    assert response["Location"] == reverse(
        "event:activity_detail", args=[activities[0].pk, activities[0].slug]
    )


# TODO: test create/update activity with organization where user isn't admin


def test_activity_create_invalid(client, activity_data):
    assert Activity.objects.count() == 0
    data = activity_data
    data["name"] = ""
    response = client.post(reverse("event:activity_create"), data)
    html = response.content.decode()
    assert response.status_code == 200
    assert Activity.objects.count() == 0
    assert "Ce champ est obligatoire." in html


def test_get_activity_update(client, activity_factory):
    activity = activity_factory()
    response = client.get(reverse("event:activity_edit", args=[activity.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert f"Mise à jour de '{activity.name}'" in html


def test_activity_update(client_log, activity_factory, activity_data):
    activity = activity_factory()
    activity_data["name"] = "activity_name2"
    response = client_log.post(
        reverse("event:activity_edit", args=[activity.pk]), activity_data
    )
    activities = Activity.objects.all()
    assert response.status_code == 302
    assert len(activities) == 1
    assert activities[0].name == "activity_name2"
    assert response["Location"] == reverse(
        "event:activity_detail", args=[activities[0].pk, activities[0].slug]
    )
