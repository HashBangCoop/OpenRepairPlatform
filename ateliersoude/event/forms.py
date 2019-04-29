from django import forms
from django.forms import ModelForm

from ateliersoude.event.models import Event, Activity, Condition


class EventForm(ModelForm):
    starts_at = forms.DateTimeField()
    ends_at = forms.DateTimeField()

    class Meta:
        model = Event
        exclude = [
            "created_at",
            "updated_at",
            "slug",
            "owner",
            "registered",
            "presents",
        ]


class ActivityForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["picture"].widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Activity
        exclude = ["slug"]


class ConditionForm(ModelForm):
    class Meta:
        model = Condition
        exclude = ["slug"]
        fields = "__all__"
