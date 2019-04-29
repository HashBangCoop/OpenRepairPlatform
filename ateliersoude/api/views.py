from functools import reduce
from operator import __or__ as OR
from urllib.parse import parse_qs

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone

from ateliersoude.event.models import Event
from ateliersoude.location.models import Place
from ateliersoude.user.models import (
    CustomUser,
    Organization,
)


def list_events_in_context(
    request,
    context_pk=None,
    context_type=None,
    context_user=None,
    context_place=None,
    context_org=None,
):
    if request.method != "GET":
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        events = []
        organizations = {}
        places = {}
        activitys = {}
        today = timezone.now()

        if context_place:
            this_place = Place.objects.get(pk=context_pk)
            all_future_events = Event.objects.filter(
                location=this_place, starts_at__gte=today, published=True
            ).order_by("starts_at")

        elif context_org:
            this_organization = Organization.objects.get(pk=context_pk)
            all_future_events = Event.objects.filter(
                organization=this_organization,
                starts_at__gte=today,
                published=True,
            ).order_by("starts_at")

        elif context_user:
            lst = [
                Q(attendees__pk=context_pk),
                Q(presents__pk=context_pk),
                Q(organizers__pk=context_pk),
            ]
            all_future_events = (
                Event.objects.filter(reduce(OR, lst))
                .filter(starts_at__gte=today, published=True)
                .order_by("starts_at")
            )

        else:
            all_future_events = Event.objects.filter(
                starts_at__gte=today, published=True
            ).order_by("starts_at")

        for event in all_future_events:
            event_pk = event.pk
            event_slug = event.slug
            event_detail_url = reverse(
                "event_detail", args=[event_pk, event_slug]
            )
            event_start_timestamp = event.starts_at.timestamp() * 1000
            organization = event.organization
            place = event.location
            activity = event.type

            if organization.pk not in organizations:
                organization_slug = organization.slug
                organization_pk = organization.pk
                organization_detail_url = reverse(
                    "organization_detail",
                    args=[organization_pk, organization_slug],
                )
                organizations[organization_pk] = {
                    "pk": organization_pk,
                    "name": organization.name,
                    "slug": organization_slug,
                    "organization_detail_url": organization_detail_url,
                }

            if place.pk not in places:
                place_slug = place.slug
                place_pk = place.pk
                place_detail_url = reverse(
                    "detail", args=[place_pk, place_slug]
                )
                places[place_pk] = {
                    "pk": place_pk,
                    "name": place.name,
                    "truncated_name": place.name[0:25],
                    "slug": place_slug,
                    "place_detail_url": place_detail_url,
                }

            if activity.pk not in activitys:
                activity_slug = activity.slug
                activity_pk = activity.pk
                activity_detail_url = reverse(
                    "activity_detail", args=[activity_pk, activity_slug]
                )
                activitys[activity_pk] = {
                    "pk": activity_pk,
                    "name": activity.name,
                    "truncated_name": activity.name[0:25],
                    "slug": activity_slug,
                    "activity_detail_url": activity_detail_url,
                }

            events += [
                {
                    "pk": event.pk,
                    "title": event.activity.name,
                    "slug": event_slug,
                    "available_seats": event.available_seats,
                    "type_picture_url": event.type.picture.url,
                    "event_detail_url": event_detail_url,
                    "book_url": reverse("booking_form", args=[event_pk]),
                    "edit_url": reverse("event_edit", args=[event_pk]),
                    "organization_pk": organization.pk,
                    "place_pk": event.location.pk,
                    "type_pk": event.type.pk,
                    "published": event.published,
                    "starts_at": event.starts_at.strftime("%H:%M"),
                    "ends_at": event.ends_at.strftime("%H:%M"),
                    "start_timestamp": event_start_timestamp,
                    "user_in_attendees": request.user in event.attendees.all(),
                    "user_in_presents": request.user in event.presents.all(),
                    "user_in_organizers": request.user
                    in event.organizers.all(),
                    "day_month_str": event.starts_at.strftime("%d %B"),
                }
            ]

        return JsonResponse(
            {
                "status": "OK",
                "dates": events,
                "organizations": organizations,
                "places": places,
                "activities": activitys,
            }
        )


def add_users(request):
    if request.method != "POST":
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        request_body = request.body.decode("utf-8")
        post_data = parse_qs(request_body)
        event_pk = post_data["event_pk"][0]
        user_list = post_data["user_list"][0].split(",")
        event = Event.objects.get(pk=event_pk)
        every_attendee = (
            event.attendees.all()
            | event.presents.all()
            | event.organizers.all()
        )
        seats = event.available_seats
        presents_pk = []
        attending_pk = []

        for user_pk in user_list:
            user = CustomUser.objects.get(pk=user_pk)
            now = timezone.now()

            if event.starts_at <= now:
                event.presents.add(user)
            else:
                if user not in every_attendee:
                    print("a")
                    seats -= 1

                    event.attendees.add(user)
                    attending_pk += [user.pk]
                else:
                    event.presents.add(user)
                    presents_pk += [user.pk]

        event.available_seats = seats
        event.save()
        return JsonResponse(
            {
                "status": "OK",
                "seats": seats,
                "presents_pk": presents_pk,
                "attending_pk": attending_pk,
            }
        )
