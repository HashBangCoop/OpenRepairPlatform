from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path("", views.UserListView.as_view(), name="user_list"),
    path("userprofile/", views.user_profile, name="user_profile"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("create/", views.register, name="user_create"),
    # Organisation
    path(
        "organization/",
        views.OrganizationListView.as_view(),
        name="organization_list",
    ),
    path(
        "organization/create/",
        views.OrganizationCreateView.as_view(),
        name="organization_create",
    ),
    path(
        "organization/<int:pk>/edit/",
        views.OrganizationEditView.as_view(),
        name="organization_edit",
    ),
    path(
        "organization/<int:pk>/<slug>/",
        views.OrganizationView.as_view(),
        name="organization_detail",
    ),
    path(
        "organization_manager/<int:pk>/",
        views.OrganizationManager,
        name="organization_manager",
    ),
]
