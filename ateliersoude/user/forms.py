import secrets
import string

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


class AddUserToEventForm(UserCreateForm):
    def __init__(self):
        super().__init__()
        self.fields["first_name"].widget = forms.HiddenInput()
        self.fields["last_name"].widget = forms.HiddenInput()
        self.fields["street_address"].widget = forms.HiddenInput()
        self.fields["password1"].widget = forms.HiddenInput()
        self.fields["password2"].widget = forms.HiddenInput()

        alphabet = string.ascii_letters + string.digits
        random_password = "Aa1" + ''.join(secrets.choice(alphabet) for _ in
                                          range(20))
        self.fields["first_name"].initial = "Utilisateur"
        self.fields["last_name"].initial = "Anonyme"
        self.fields["password1"].initial = random_password
        self.fields["password2"].initial = random_password


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ["visitors", "members", "volunteers", "admins", "slug"]
