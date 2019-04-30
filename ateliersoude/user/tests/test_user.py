import pytest

from django.contrib.auth import get_user
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_user_list(client, custom_user):
    response = client.get(reverse("user:user_list"))
    assert response.status_code == 200
    assert get_user(client).is_anonymous
