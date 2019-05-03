from django.core.management import BaseCommand
from django.utils import timezone

from ateliersoude.event.models import Event


# Run every hour
# 20 * * * *
class PublishEvents(BaseCommand):
    help = "Publish non published events"

    def handle(self, *args, **options):
        unpublished_events = (Event.objects
                              .filter(published=False)
                              .filter(publish_at__lte=timezone.now())
                              )
        for event in unpublished_events:
            event.published = True
            event.save()

