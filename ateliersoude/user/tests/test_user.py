import pytest

from django.contrib.auth import get_user
from django.urls import reverse

from ateliersoude.location.models import Place

pytestmark = pytest.mark.django_db


def test_user_list(client):
    response = client.get(reverse("location:place_list"))
    assert response.status_code == 200
    assert get_user(client).is_anonymous


def test_user_detail(client):
    response = client.get(reverse("location:place_list"))
    assert response.status_code == 200
    assert get_user(client).is_anonymous
