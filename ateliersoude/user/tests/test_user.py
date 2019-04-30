import pytest
from django.core.management.base import CommandError
from django.core.management import call_command
from django.urls import reverse
from ateliersoude.user.models import CustomUser

pytestmark = pytest.mark.django_db

USER_PASSWORD = "hackmeplease2048"


def test_command_superuser():
    assert CustomUser.objects.count() == 0
    call_command("createsuperuser", email="test@test.com", interactive=False)
    assert CustomUser.objects.count() == 1


def test_command_superuser_without_mail():
    assert CustomUser.objects.count() == 0
    with pytest.raises(CommandError):
        call_command("createsuperuser", email="", interactive=False)


def test_user_list(client, custom_user):
    response = client.get(reverse("user:user_list"))
    assert response.status_code == 200
    response.context_data["object_list"].count() == 1


def test_user_detail(client, custom_user):
    response = client.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 200


def test_user_create(client, custom_user):
    assert CustomUser.objects.count() == 1
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
    assert CustomUser.objects.count() == 2


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
