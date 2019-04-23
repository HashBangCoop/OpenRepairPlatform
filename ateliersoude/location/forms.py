from django import forms
from django.forms import ModelForm

from ateliersoude.location.models import Place


class PlaceForm(ModelForm):
    description = forms.CharField(widget=forms.Textarea)
    longitude = forms.CharField(widget=forms.HiddenInput)
    latitude = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Place
        exclude = ["created_at", "updated_at", "slug", "owner"]
