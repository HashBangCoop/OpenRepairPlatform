import datetime

from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.utils import timezone

from ateliersoude.event.models import Event


# Run every day at a given time
# 10 16 * * *
class NotifyEventIncoming(BaseCommand):
    help = "Send email to all registered users the day before the event"

    def handle(self, *args, **options):
        now = timezone.now()
        tomorrow_23h59 = now + datetime.timedelta(days=1)
        tomorrow_23h59 = tomorrow_23h59.replace(hour=23, minute=59, second=59)
        events_next_day = Event.objects.filter(published=True)\
            .filter(publish_at__lte=now)\
            .filter(ends_at__gte=now)\
            .filter(starts_at__lte=tomorrow_23h59)
        for event in events_next_day:
            for user in event.registered:
                subject = ""
                msg_plain = ""
                msg_html = ""
                send_mail(
                    subject,
                    msg_plain,
                    "no-reply@atelier-soude.fr",
                    [user.email],
                    html_message=msg_html,
                )

