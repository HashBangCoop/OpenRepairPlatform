from django import forms
from django.forms import ModelForm

from ateliersoude.event.models import Event, Activity, Condition


class EventForm(ModelForm):
    starts_at = forms.DateTimeField()
    ends_at = forms.DateTimeField()

    def __init__(self, *args, **kwargs):
        orga = kwargs.pop('orga')
        super().__init__(*args, **kwargs)
        self.fields['organizers'] = forms.ModelMultipleChoiceField(
            queryset=(orga.volunteers.all() | orga.admins.all()).distinct(),
            widget=forms.CheckboxSelectMultiple,
        )
        self.fields['conditions'] = forms.ModelMultipleChoiceField(
            queryset=orga.conditions,
            widget=forms.CheckboxSelectMultiple,
        )

    class Meta:
        model = Event
        exclude = [
            "created_at",
            "updated_at",
            "slug",
            "owner",
            "registered",
            "presents",
            "organization",
        ]


class ActivityForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["picture"].widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Activity
        exclude = ["slug", "organization"]


class ConditionForm(ModelForm):
    class Meta:
        model = Condition
        exclude = ["slug", "organization"]
