import pytest
from django.core import signing

from ateliersoude import settings
from ateliersoude.event.templatetags.app_filters import tokenize

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
