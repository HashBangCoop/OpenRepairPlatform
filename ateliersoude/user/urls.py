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
    path("create_and_book/", views.UserCreateAndBookView.as_view(),
         name="create_and_book"),
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
    path(
        "organization/<int:orga_pk>/add-admin",
        views.AddAdminToOrganization.as_view(),
        name="organization_add_admin",
    ),
    path(
        "organization/<int:orga_pk>/add-volunteer",
        views.AddVolunteerToOrganization.as_view(),
        name="organization_add_volunteer",
    ),
    path(
        "organization/<int:orga_pk>/<int:user_pk>/remove-from-volunteers",
        views.RemoveVolunteerFromOrganization.as_view(),
        name="remove_from_volunteers",
    ),
    path(
        "organization/<int:orga_pk>/<int:user_pk>/remove-from-admins",
        views.RemoveAdminFromOrganization.as_view(),
        name="remove_from_admins",
    ),
]
