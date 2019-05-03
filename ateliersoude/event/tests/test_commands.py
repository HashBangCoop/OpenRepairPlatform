import datetime

import pytest
from django.core.management import call_command
from django.utils import timezone

pytestmark = pytest.mark.django_db

sendmail_count = 0


def mocked_send_mail(*args, **kwargs):
    subject, plain, from_email, recipients = args
    _ = kwargs.pop("html_message")
    global sendmail_count
    sendmail_count += 1


def test_command_notify_next_day_events(published_event_factory, user_log):
    event1 = published_event_factory(
        starts_at=timezone.now() + datetime.timedelta(days=1),
    )
    event1.registered.add(user_log)
    from django.core import mail
    mail.send_mail = mocked_send_mail
    call_command("notify_next_day_events", "https://example.com")
    global sendmail_count
    assert sendmail_count == 1
    sendmail_count = 0


def test_command_publish_events(event_factory):
    event1 = event_factory(
        published=False,
        publish_at=timezone.now() - timezone.timedelta(hours=1)
    )
    call_command("publish_events")
    event1.refresh_from_db()
    assert event1.published
