from django.urls import path

from . import views

urlpatterns = [
    path("", views.UserListView.as_view(), name="user_list"),
    path("userprofile/", views.user_profile, name="user_profile"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("create/", views.register, name="user_create"),
]
