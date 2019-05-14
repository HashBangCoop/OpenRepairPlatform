from django import forms
from django.forms import ModelForm

from ateliersoude.event.models import Event, Activity, Condition
from ateliersoude.location.models import Place
from ateliersoude.user.models import Organization


class EventForm(ModelForm):
    starts_at = forms.DateTimeField()
    ends_at = forms.DateTimeField()

    def __init__(self, *args, **kwargs):
        self.orga = kwargs.pop("orga")
        super().__init__(*args, **kwargs)
        self.fields["organizers"] = forms.ModelMultipleChoiceField(
            queryset=(
                self.orga.volunteers.all() | self.orga.admins.all()
            ).distinct(),
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )
        self.fields["conditions"] = forms.ModelMultipleChoiceField(
            queryset=self.orga.conditions,
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )

    class Meta:
        model = Event

        fields = [
            "activity",
            "location",
            "available_seats",
            "starts_at",
            "ends_at",
            "publish_at",
            "organizers",
            "conditions",
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


class EventSearchForm(forms.Form):
    starts_after = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        required=False,
    )
    starts_before = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        future_events = Event.future_published_events()
        self.fields["place"] = forms.ModelChoiceField(
            required=False,
            queryset=Place.objects.filter(events__in=future_events),
        )
        self.fields["organization"] = forms.ModelChoiceField(
            required=False,
            queryset=Organization.objects.filter(events__in=future_events),
        )
        self.fields["activity"] = forms.ModelChoiceField(
            required=False,
            queryset=Activity.objects.filter(events__in=future_events),
        )
