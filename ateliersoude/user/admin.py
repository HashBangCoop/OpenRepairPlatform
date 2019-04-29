from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _

from .models import CustomUser, Organization
from .forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
            "fields": (
                "first_name",
                "last_name",
                "phone_number",
                "street_address",
                "birth_date",
                "bio",
            )
        }),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_staff")
    add_fieldsets = ((None, {
        "classes": ("wide",),
        "fields": ("email", "password1", "password2"),
    }),)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization)
