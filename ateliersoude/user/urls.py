from django.urls import path

from . import views

app_name = "user"
urlpatterns = [
    path("", views.UserListView.as_view(), name="user_list"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path(
        "update/<int:pk>", views.UserUpdateView.as_view(), name="user_update"
    ),
    path("create/", views.UserCreateView.as_view(), name="user_create"),
    path(
        "organizations/",
        views.OrganizationListView.as_view(),
        name="organization_list",
    ),
    path(
        "organization/create/",
        views.OrganizationCreateView.as_view(),
        name="organization_create",
    ),
    path(
        "organization/<int:pk>/update/",
        views.OrganizationUpdateView.as_view(),
        name="organization_update",
    ),
    path(
        "organization/<int:pk>/<slug>/",
        views.OrganizationDetailView.as_view(),
        name="organization_detail",
    ),
    path(
        "organization/<int:pk>/",
        views.OrganizationDeleteView.as_view(),
        name="organization_delete",
    ),
]