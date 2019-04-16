from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .forms import CustomUserChangeForm, CustomUserCreationForm

from .models import (
    CustomUser,
    Organization,
    OrganizationPerson,
)


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "street_address",
                    "birth_date",
                    "bio",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": (
                "wide",), "fields": (
                "email", "password1", "password2")}), )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "active")


class OrganizationPersonAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role")


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationPerson, OrganizationPersonAdmin)
