import pytest
from django.contrib.auth import get_user
from django.urls import reverse

from ateliersoude.event.models import Condition

pytestmark = pytest.mark.django_db


@pytest.fixture
def condition_data(organization_factory):
    orga = organization_factory()
    return {
        "name": "cond_name",
        "organization": orga.pk,
        "price": 12.13,
        "description": "Lorem ipsum",
    }


def test_condition_list(client, condition_factory):
    response = client.get(reverse("event:condition_list"))
    assert response.status_code == 200
    assert get_user(client).is_anonymous
    assert "Aucune condition trouvée" in response.content.decode()
    condition = condition_factory()
    response = client.get(reverse("event:condition_list"))
    assert condition.name in response.content.decode()
    assert condition.description in response.content.decode()


def test_get_condition_delete(client, condition_factory):
    condition = condition_factory()
    response = client.get(
        reverse("event:condition_delete", args=[condition.pk])
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert condition.name in html
    assert condition.organization.name in html


def test_condition_delete(client, condition_factory):
    condition = condition_factory()
    assert Condition.objects.count() == 1
    response = client.post(
        reverse("event:condition_delete", args=[condition.pk])
    )
    assert Condition.objects.count() == 0
    assert response.status_code == 302
    assert response["Location"] == reverse(
        "user:organization_detail",
        args=[condition.organization.pk, condition.organization.slug],
    )


def test_get_condition_create(client):
    response = client.get(reverse("event:condition_create"))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Création d'une nouvelle Condition" in html


def test_condition_create(client_log, condition_data):
    assert Condition.objects.count() == 0
    response = client_log.post(
        reverse("event:condition_create"), condition_data
    )
    conditions = Condition.objects.all()
    assert response.status_code == 302
    assert len(conditions) == 1
    orga = conditions[0].organization
    assert response["Location"] == reverse(
        "user:organization_detail", args=[orga.pk, orga.slug]
    )


# TODO: test create/update condition with organization where user isn't admin


def test_condition_create_invalid(client, condition_data):
    assert Condition.objects.count() == 0
    data = condition_data
    data["name"] = ""
    response = client.post(reverse("event:condition_create"), data)
    html = response.content.decode()
    assert response.status_code == 200
    assert Condition.objects.count() == 0
    assert "Ce champ est obligatoire." in html


def test_get_condition_update(client, condition_factory):
    condition = condition_factory()
    response = client.get(reverse("event:condition_edit", args=[condition.pk, condition.organization.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert f"Mise à jour de '{condition.name}'" in html


def test_condition_update(client_log, condition_factory, condition_data):
    condition = condition_factory()
    condition_data["name"] = "cond_name2"
    response = client_log.post(
        reverse("event:condition_edit", args=[condition.pk, condition.organization.pk]), condition_data
    )
    conditions = Condition.objects.all()
    assert response.status_code == 302
    assert len(conditions) == 1
    orga = conditions[0].organization
    assert conditions[0].name == "cond_name2"
    assert response["Location"] == reverse(
        "user:organization_detail", args=[orga.pk, orga.slug]
    )
