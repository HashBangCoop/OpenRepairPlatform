import pytest
from django.core import signing

from ateliersoude import settings
from ateliersoude.event.templatetags.app_filters import serialize_id

pytestmark = pytest.mark.django_db


def test_serialize_id():
    user_id = 1
    event_id = 2
    signed = serialize_id(user_id, event_id)
    data = {"user_id": user_id, "event_id": event_id}
    signed_expected = signing.dumps(data, key=settings.SECRET_KEY)
    assert signed == signed_expected
    assert signing.loads(signed, key=settings.SECRET_KEY) == data
