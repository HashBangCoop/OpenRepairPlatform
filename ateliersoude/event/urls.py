from django.urls import path

from . import views

app_name = "event"
urlpatterns = [
    path(
        "condition/create/",
        views.ConditionCreateView.as_view(),
        name="condition_create",
    ),
    path(
        "condition/<int:pk>/edit/",
        views.ConditionEditView.as_view(),
        name="condition_edit",
    ),
    path("activity/",
         views.ActivityListView.as_view(),
         name="activity_list"),
    path(
        "activity/create/",
        views.ActivityCreateView.as_view(),
        name="activity_create",
    ),
    path(
        "activity/<int:pk>/edit/",
        views.ActivityEditView.as_view(),
        name="activity_edit",
    ),
    path(
        "activity/<int:pk>/<slug>/",
        views.ActivityView.as_view(),
        name="activity_detail",
    ),
    path("event/", views.EventListView.as_view(), name="event_list"),
    path("event/create/",
         views.EventCreateView.as_view(),
         name="event_create"),
    path(
        "event/cancel_reservation/<token>/",
        views.cancel_reservation,
        name="cancel_reservation",
    ),
    path(
        "event/<int:pk>/book/",
        views.BookingEditView.as_view(),
        name="booking_form",
    ),
    path(
        "event/<int:pk>/edit/",
        views.EventEditView.as_view(),
        name="event_edit",
    ),
    path(
        "event/<int:pk>/<slug>/",
        views.EventView.as_view(),
        name="event_detail",
    ),
    path(
        "massevent/book/",
        views.MassBookingCreateView.as_view(),
        name="mass_event_book",
    ),
]
