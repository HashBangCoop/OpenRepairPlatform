from typing import Optional
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.urls import resolve, Resolver404, ResolverMatch
from django.utils import timezone

MAX_SIZE_MB = 1


def validate_image(image):
    file_size = image.file.size
    if file_size > MAX_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"La taille maximale d'une image est de " f"{MAX_SIZE_MB}MB"
        )


def get_future_published_events(events_objects):
    """Filters the events to fetch only the future published events"""
    return (
        events_objects.filter(published=True)
        .filter(publish_at__lte=timezone.now())
        .filter(ends_at__gte=timezone.now())
    )


def get_referer_resolver(request: HttpRequest) -> Optional[ResolverMatch]:
    """
    Return the referer's ResolverMatch
    """
    referer = request.META.get("HTTP_REFERER")
    if not referer:
        return None

    url = urlparse(referer)
    if url.netloc != request.get_host():
        return None

    try:
        return resolve(url.path)
    except Resolver404:
        return None
