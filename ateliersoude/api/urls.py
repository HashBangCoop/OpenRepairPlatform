from django.urls import path

from . import views

urlpatterns = [
    path("deleteEvent/", views.delete_event, name="delete_event"),
    path("setPresent/", views.set_present, name="set_present"),
    path("setAbsent/", views.set_absent, name="set_absent"),
    path(
        "getOrganizations/", views.get_organizations, name="get_organizations"
    ),
    path(
        "getPlacesForOrganization/",
        views.get_places_for_organization,
        name="get_places_for_organization",
    ),
    path("getDates/", views.get_dates, name="get_dates"),
    path(
        "getUsers/<int:organization_pk>/(<int:event_pk>/",
        views.list_users,
        name="list_users",
    ),
    path("addUsers/", views.add_users, name="add_users"),
    path(
        "list_events/",
        views.list_events_in_context,
        name="list_events_in_context",
    ),
    path(
        "list_events_user/<int:context_pk>/",
        views.list_events_in_context,
        {"context_user": "yes"},
        name="list_events_user",
    ),
    path(
        "list_events_place/<int:context_pk>/",
        views.list_events_in_context,
        {"context_place": "yes"},
        name="list_events_place",
    ),
    path(
        "list_events_organization/<int:context_pk>/",
        views.list_events_in_context,
        {"context_org": "yes"},
        name="list_events_organization",
    ),
    path("book/", views.book_event, name="book"),
]
