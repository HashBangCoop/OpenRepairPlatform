from os.path import join, dirname, abspath

import pytest

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ateliersoude.user.factories import USER_PASSWORD
from ateliersoude.user.models import Organization

pytestmark = pytest.mark.django_db
FILES_DIR = join(dirname(abspath(__file__)), "files")


def test_organization_list(client, organization):
    response = client.get(reverse("user:organization_list"))
    assert response.status_code == 200
    assert response.context_data["object_list"].count() == 1


def test_organization_detail(client, organization):
    response = client.get(
        reverse(
            "user:organization_detail",
            kwargs={"pk": organization.pk, "slug": organization.slug},
        )
    )
    assert response.status_code == 200


def test_organization_create(client_log, organization):
    assert Organization.objects.count() == 1
    image_file = File(open(join(FILES_DIR, "test.png"), "rb"))
    upload_image = SimpleUploadedFile(
        "image.png", image_file.read(), content_type="multipart/form-data"
    )
    response = client_log.post(
        reverse("user:organization_create"),
        {"name": "Test", "description": "Orga test", "picture": upload_image},
    )
    assert response.status_code == 302
    assert "organization" in response.url
    assert Organization.objects.count() == 2


def test_organization_update(client_log, organization):
    response = client_log.post(
        reverse("user:organization_update", kwargs={"pk": organization.pk}),
        {"name": "Test Orga", "description": "Test"},
    )
    assert response.status_code == 302
    organization.refresh_from_db()
    assert response.url == reverse(
        "user:organization_detail",
        kwargs={"pk": organization.pk, "slug": organization.slug},
    )
    assert organization.name == "Test Orga"


def test_organization_delete(client_log, organization):
    assert Organization.objects.count() == 1
    response = client_log.post(
        reverse("user:organization_delete", kwargs={"pk": organization.pk})
    )
    assert response.status_code == 302
    assert response.url == reverse("user:organization_list")
    assert Organization.objects.count() == 0


def test_add_admin_to_organization_forbidden(client, user_log, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse(
            "user:organization_add_admin", kwargs={"orga_pk": organization.pk}
        ),
        {"email": user_log.email},
    )
    assert response.status_code == 403


def test_add_admin_to_organization(custom_user_factory, client, organization):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.admins.count() == 1
    response = client.post(
        reverse(
            "user:organization_add_admin", kwargs={"orga_pk": organization.pk}
        ),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "user:organization_detail",
        kwargs={"pk": organization.pk, "slug": organization.slug},
    )
    assert organization.admins.count() == 2


def test_add_admin_to_organization_wrong_user(
    custom_user, client, organization
):
    organization.admins.add(custom_user)
    assert client.login(email=custom_user.email, password=USER_PASSWORD)
    assert organization.admins.count() == 1
    response = client.post(
        reverse(
            "user:organization_add_admin", kwargs={"orga_pk": organization.pk}
        ),
        {"email": "unknown@something.org"},
    )
    assert response.status_code == 302
    assert organization.admins.count() == 1


def test_add_volunteer_to_organization_forbidden(
    client, user_log, organization
):
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse(
            "user:organization_add_volunteer",
            kwargs={"orga_pk": organization.pk},
        ),
        {"email": user_log.email},
    )
    assert response.status_code == 403


def test_add_volunteer_to_organization(
    custom_user_factory, client, organization
):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.volunteers.count() == 0
    response = client.post(
        reverse(
            "user:organization_add_volunteer",
            kwargs={"orga_pk": organization.pk},
        ),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "user:organization_detail",
        kwargs={"pk": organization.pk, "slug": organization.slug},
    )
    volunteers = organization.volunteers.all()
    assert len(volunteers) == 1
    assert volunteers[0].pk == user.pk


def test_add_admin_to_volunteers_of_organization(
    custom_user_factory, client, organization
):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    organization.admins.add(user)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.volunteers.count() == 0
    response = client.post(
        reverse(
            "user:organization_add_volunteer",
            kwargs={"orga_pk": organization.pk},
        ),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "user:organization_detail",
        kwargs={"pk": organization.pk, "slug": organization.slug},
    )
    assert organization.volunteers.count() == 0


def test_add_volunteer_to_admins_of_organization(
    custom_user_factory, client, organization
):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    organization.volunteers.add(user)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.volunteers.count() == 1
    assert organization.admins.count() == 1
    response = client.post(
        reverse(
            "user:organization_add_admin",
            kwargs={"orga_pk": organization.pk},
        ),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "user:organization_detail",
        kwargs={"pk": organization.pk, "slug": organization.slug},
    )
    assert organization.volunteers.count() == 0
    assert organization.admins.count() == 2


def test_remove_volunteer_from_organization_forbidden(
    client, user_log, organization
):
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse(
            "user:remove_from_volunteers",
            kwargs={
                "orga_pk": organization.pk,
                "user_pk": 123,  # we don't care, we'll get a 403 anyway
            },
        )
    )
    assert response.status_code == 403


def test_remove_volunteer_from_organization(
    custom_user_factory, client, organization
):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.volunteers.add(user)
    organization.admins.add(admin)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.volunteers.count() == 1
    response = client.post(
        reverse(
            "user:remove_from_volunteers",
            kwargs={"orga_pk": organization.pk, "user_pk": user.pk},
        )
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "user:organization_detail",
        kwargs={"pk": organization.pk, "slug": organization.slug},
    )
    assert organization.volunteers.count() == 0


def test_remove_admin_from_organization(
    custom_user_factory, client, organization
):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    organization.admins.add(user)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.admins.count() == 2
    response = client.post(
        reverse(
            "user:remove_from_admins",
            kwargs={"orga_pk": organization.pk, "user_pk": user.pk},
        )
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "user:organization_detail",
        kwargs={"pk": organization.pk, "slug": organization.slug},
    )
    assert organization.admins.count() == 1
