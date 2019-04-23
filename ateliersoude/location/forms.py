from django import forms
from django.forms import ModelForm

from ateliersoude.location.models import Place


class PlaceForm(ModelForm):
    description = forms.CharField(widget=forms.Textarea)
    longitude = forms.CharField(widget=forms.HiddenInput)
    latitude = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        picture_widget = self.fields["picture"].widget
        existing_classes = picture_widget.attrs.get("class", "")
        picture_widget.attrs.update({
            "class": f"{existing_classes} form-control".strip()
        })

    class Meta:
        model = Place
        exclude = ["created_at", "updated_at", "slug", "owner"]
