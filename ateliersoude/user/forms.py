from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser, Organization


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email"]


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser


class UserCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "street_address"]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "street_address",
            "birth_date",
            "gender",
            "bio",
        ]
        widgets = {
            "birth_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            )
        }


class AddUserToEventForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email"]


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ["visitors", "members", "volunteers", "admins", "slug"]
