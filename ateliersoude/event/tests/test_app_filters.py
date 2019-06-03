import pytest
from django.core import signing

from ateliersoude import settings
from ateliersoude.event.models import Event
from ateliersoude.event.templatetags.app_filters import (
    tokenize,
    initial,
    filter_orga,
)
from ateliersoude.user.forms import MoreInfoCustomUserForm

pytestmark = pytest.mark.django_db


class MockId:
    def __init__(self, id):
        self.id = id


def test_token():
    signed = tokenize(MockId(1), MockId(2), "book")
    data = {"user_id": 1, "event_id": 2}
    signed_expected = signing.dumps(data, key=settings.SECRET_KEY, salt="book")
    assert signed == signed_expected
    assert signing.loads(signed, key=settings.SECRET_KEY, salt="book") == data


def test_initial(custom_user):
    form = MoreInfoCustomUserForm()
    assert form.initial.get("email") is None
    form = initial(form, custom_user)
    assert form.initial["email"] == custom_user.email


def test_filter_orga(organization, event_factory):
    _ = event_factory()
    event1 = event_factory(organization=organization)
    _ = event_factory()
    a = filter_orga(Event.objects, organization)
    assert a.pk == event1.pk
