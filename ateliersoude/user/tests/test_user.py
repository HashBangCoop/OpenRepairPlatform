import datetime
from urllib.parse import urlparse

import pytest
from django.contrib.auth import get_user
from django.core.management.base import CommandError
from django.core.management import call_command
from django.urls import reverse, resolve
from django.utils import timezone

from ateliersoude.event.views import _load_token
from ateliersoude.user.factories import USER_PASSWORD
from ateliersoude.user.models import CustomUser

pytestmark = pytest.mark.django_db


def test_command_superuser():
    assert CustomUser.objects.count() == 0
    call_command("createsuperuser", email="test@test.com", interactive=False)
    assert CustomUser.objects.count() == 1


def test_command_superuser_without_mail():
    assert CustomUser.objects.count() == 0
    with pytest.raises(CommandError):
        call_command("createsuperuser", email="", interactive=False)


def test_user_list_not_visible(client, custom_user):
    response = client.get(reverse("user:user_list"))
    assert response.status_code == 200
    assert response.context_data["object_list"].count() == 0


def test_user_list_visible(client, custom_user):
    custom_user.is_visible = True
    custom_user.save()
    response = client.get(reverse("user:user_list"))
    assert response.status_code == 200
    assert response.context_data["object_list"].count() == 1


def test_user_detail_not_visible(client, custom_user):
    response = client.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 404


def test_user_detail_visible(client, custom_user):
    custom_user.is_visible = True
    custom_user.save()
    response = client.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 200


def test_user_detail_not_visible_but_staff(client_log, custom_user):
    user = get_user(client_log)
    user.is_staff = True
    user.save()
    response = client_log.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 200


def test_user_detail_not_visible_but_same(client, custom_user):
    client.login(email=custom_user.email, password=USER_PASSWORD)
    response = client.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 200


def test_user_detail_not_visible_but_volunteer(client_log, custom_user,
                                               event_factory, organization):
    user = get_user(client_log)
    organization.volunteers.add(user)
    event = event_factory(organization=organization)
    event.registered.add(custom_user)
    response = client_log.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 200


def test_user_create(client):
    assert CustomUser.objects.count() == 0
    response = client.post(
        reverse("user:user_create"),
        {
            "email": "test@test.fr",
            "first_name": "Test",
            "last_name": "Test",
            "street_address": "221 b Tester Street",
            "password1": USER_PASSWORD,
            "password2": USER_PASSWORD,
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("login")
    assert CustomUser.objects.count() == 1


def test_anonymous_user_create(client, event):
    assert CustomUser.objects.count() == 0
    response = client.post(
        reverse("user:create_and_book") + f"?event={event.pk}",
        {"email": "test@test.fr"},
    )
    anonymous_user = CustomUser.objects.first()
    assert response.status_code == 302
    url_parsed = urlparse(response.url)
    resolved = resolve(url_parsed.path)
    event_from_token, user = _load_token(resolved.kwargs["token"], "book")
    assert anonymous_user.first_name == ""
    assert anonymous_user.password == ""
    assert event.pk == event_from_token.pk


def test_anonymous_user_create_already_exists(client, event, custom_user):
    response = client.post(
        reverse("user:create_and_book") + f"?event={event.pk}",
        {"email": custom_user.email},
    )
    user = CustomUser.objects.first()
    assert response.status_code == 302
    assert user.pk == custom_user.pk
    url_parsed = urlparse(response.url)
    resolved = resolve(url_parsed.path)
    event_from_token, user = _load_token(resolved.kwargs["token"], "book")
    assert custom_user.first_name == user.first_name
    assert custom_user.password == user.password
    assert event.pk == event_from_token.pk


def test_anonymous_get_user_create(client, event_factory, organization):
    in_two_hours = timezone.now() + datetime.timedelta(hours=2)
    two_hours_ago = timezone.now() - datetime.timedelta(hours=2)
    event_factory(
        organization=organization,
        starts_at=in_two_hours,
        publish_at=two_hours_ago,
    )
    response = client.get(
        reverse(
            "user:organization_detail",
            kwargs={"pk": organization.pk, "slug": organization.slug},
        )
    )
    assert response.status_code == 200


def test_user_update(client, custom_user):
    response = client.post(
        reverse("user:user_update", kwargs={"pk": custom_user.pk}),
        {
            "first_name": "Test",
            "last_name": "Test",
            "email": "test@test.fr",
            "street_address": "221 b Tester Street",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "user:user_detail", kwargs={"pk": custom_user.pk}
    )
    custom_user.refresh_from_db()
    assert custom_user.first_name == "Test"
