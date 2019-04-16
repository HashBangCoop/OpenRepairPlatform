from django.urls import path

from . import views

app_name = "location"
urlpatterns = [
    path("place/", views.PlaceListView.as_view(), name="place_list"),
    path("place/create/",
         views.PlaceCreateView.as_view(),
         name="place_create"),
    path(
        "place/<int:pk>/edit/",
        views.PlaceEditView.as_view(),
        name="place_edit",
    ),
    path(
        "place/<int:pk>/<slug>/",
        views.PlaceView.as_view(),
        name="place_detail",
    ),
]
