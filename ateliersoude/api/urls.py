from django.urls import path

from . import views

urlpatterns = [
    path("addUsers/", views.add_users, name="add_users"),
    path(
        "list_events/",
        views.list_events_in_context,
        name="list_events_in_context",
    ),
]
