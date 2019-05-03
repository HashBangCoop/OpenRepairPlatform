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


class EventSearchForm(forms.Form):
    place = forms.ChoiceField(required=False)
    organization = forms.ChoiceField(required=False)
    activity = forms.ChoiceField(required=False)
    starts_before = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        required=False,
    )
    starts_after = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        empty = [("", "---")]
        places = list(Place.objects.all())
        orgas = list(Organization.objects.all())
        future_events = Event.future_published_events()
        activities = {
            evt.activity.name.lower().title() for evt in future_events
        }
        self.fields["place"].choices = empty + [(p.pk, p) for p in places]
        self.fields["organization"].choices = empty + [
            (o.pk, o) for o in orgas
        ]
        self.fields["activity"].choices = empty + [(a, a) for a in activities]
