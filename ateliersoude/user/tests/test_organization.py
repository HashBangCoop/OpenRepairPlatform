from os.path import join, dirname, abspath

import pytest

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ateliersoude.user.models import Organization

pytestmark = pytest.mark.django_db

USER_PASSWORD = "hackmeplease2048"
FILES_DIR = join(dirname(abspath(__file__)), "files")


def test_organization_list(client, organization):
    response = client.get(reverse("user:organization_list"))
    assert response.status_code == 200
    response.context_data["object_list"].count() == 1


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
