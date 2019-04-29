import pytest

from django.contrib.auth import get_user
from django.urls import reverse

from ateliersoude.location.models import Place

pytestmark = pytest.mark.django_db


@pytest.fixture
def location_data(organization_factory):
    orga = organization_factory()
    return {
        "name": "myname",
        "category": "test",
        "address": "1, rue Sylvestre",
        "organization": orga.pk,
        "longitude": 12,
        "latitude": 21,
        "description": "Lorem ipsum",
    }


def test_location_list(client):
    response = client.get(reverse("location:list"))
    assert response.status_code == 200
    assert get_user(client).is_anonymous


def test_location_api_list(client, place_factory):
    response = client.get(reverse("api_location:places"))
    places = response.json()
    assert response.status_code == 200
    assert len(places) == 0
    place = place_factory()
    response = client.get(reverse("api_location:places"))
    places = response.json()
    assert len(places) == 1
    assert places[0]["name"] == place.name
    assert places[0].keys() == {
        "picture",
        "get_absolute_url",
        "orga_url",
        "orga_name",
        "name",
        "address",
        "latitude",
        "longitude",
        "category",
    }


def test_location_detail_context(client, place_factory):
    place = place_factory()
    response = client.get(
        reverse("location:detail", args=[place.pk, place.slug])
    )
    assert response.status_code == 200
    assert isinstance(response.context_data["place"], Place)
    assert place.pk == response.context_data["place"].pk
    assert place.name == str(response.context_data["place"])


def test_get_location_delete(client, place_factory):
    place = place_factory()
    response = client.get(reverse("location:delete", args=[place.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert place.name in html
    assert place.address in html


def test_location_delete(client, place_factory):
    place = place_factory()
    assert Place.objects.count() == 1
    response = client.post(reverse("location:delete", args=[place.pk]))
    assert Place.objects.count() == 0
    assert response.status_code == 302
    assert response["Location"] == reverse("location:list")


def test_get_location_create(client):
    response = client.get(reverse("location:create"))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Création d'un nouveau lieu" in html


def test_location_create(client_log, location_data):
    assert Place.objects.count() == 0
    response = client_log.post(reverse("location:create"), location_data)
    places = Place.objects.all()
    assert response.status_code == 302
    assert len(places) == 1
    assert response["Location"] == reverse(
        "location:detail", args=[places[0].pk, places[0].slug]
    )


def test_location_create_invalid(client, location_data):
    assert Place.objects.count() == 0
    data = location_data
    data["name"] = ""
    response = client.post(reverse("location:create"), data)
    html = response.content.decode()
    assert response.status_code == 200
    assert Place.objects.count() == 0
    assert "Ce champ est obligatoire." in html


def test_get_location_update(client, place_factory):
    place = place_factory()
    response = client.get(reverse("location:edit", args=[place.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert f"Mise à jour de '{place.name}'" in html


def test_location_update(client_log, place_factory, location_data):
    place = place_factory()
    response = client_log.post(
        reverse("location:edit", args=[place.pk]), location_data
    )
    places = Place.objects.all()
    assert response.status_code == 302
    assert len(places) == 1
    assert places[0].name == "myname"
    assert response["Location"] == reverse(
        "location:detail", args=[places[0].pk, places[0].slug]
    )


# TODO: test create/update activity with organization where user isn't admin
