import pytest
from django.contrib.auth import get_user
from django.urls import reverse

from ateliersoude.event.models import Activity
from ateliersoude.user.factories import USER_PASSWORD

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


def test_get_activity_create(client, user_log, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    response = client.get(
        reverse("event:activity_create", args=[organization.pk])
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert "Création d'une nouvelle activité" in html


def test_get_activity_create_403(client, organization):
    response = client.get(
        reverse("event:activity_create", args=[organization.pk])
    )
    html = response.content.decode()
    assert response.status_code == 403
    assert "Vous ne pouvez pas créer" in html


def test_get_activity_create_403_not_in_orga(client_log, organization):
    response = client_log.get(
        reverse("event:activity_create", args=[organization.pk])
    )
    html = response.content.decode()
    assert response.status_code == 403
    assert "Vous ne pouvez pas créer" in html


def test_activity_create(client, user_log, organization, activity_data):
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    assert Activity.objects.count() == 0
    response = client.post(
        reverse("event:activity_create", args=[organization.pk]), activity_data
    )
    activities = Activity.objects.all()
    assert response.status_code == 302
    assert len(activities) == 1
    assert response["Location"] == reverse(
        "event:activity_detail", args=[activities[0].pk, activities[0].slug]
    )


def test_activity_create_invalid(
    user_log, client, activity_data, organization
):
    assert Activity.objects.count() == 0
    data = activity_data
    data["name"] = ""
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    response = client.post(
        reverse("event:activity_create", args=[organization.pk]), data
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert Activity.objects.count() == 0
    assert "Ce champ est obligatoire." in html


def test_get_activity_update_403(client, organization, activity):
    response = client.get(
        reverse("event:activity_edit", args=[activity.pk, organization.pk])
    )
    html = response.content.decode()
    assert response.status_code == 403
    assert "Vous ne pouvez pas créer" in html


def test_get_activity_update_403_not_in_orga(
    client_log, organization, activity
):
    response = client_log.get(
        reverse("event:activity_edit", args=[activity.pk, organization.pk])
    )
    html = response.content.decode()
    assert response.status_code == 403
    assert "Vous ne pouvez pas créer" in html


def test_get_activity_update(user_log, client, activity, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    response = client.get(
        reverse("event:activity_edit", args=[activity.pk, organization.pk])
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert f"Mise à jour de '{activity.name}'" in html


def test_activity_update(
    user_log, client, activity, activity_data, organization
):
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    activity_data["name"] = "activity_name2"
    response = client.post(
        reverse("event:activity_edit", args=[activity.pk, organization.pk]),
        activity_data,
    )
    activities = Activity.objects.all()
    assert response.status_code == 302
    assert len(activities) == 1
    assert activities[0].name == "activity_name2"
    assert response["Location"] == reverse(
        "event:activity_detail", args=[activities[0].pk, activities[0].slug]
    )
