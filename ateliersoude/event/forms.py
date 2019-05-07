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


class RecurrentEventForm(forms.ModelForm):
    starts_at = forms.TimeField()
    ends_at = forms.TimeField()
    recurrent_type = forms.ChoiceField(
        choices=[("week", "Par semaine"), ("month", "Par mois")],
        label="Type de récurrence",
    )
    publish_date = forms.ChoiceField(
        choices=[
            ("1d", "1 jour avant"),
            ("2d", "2 jours avant"),
            ("1w", "Une semaine avant"),
            ("2w", "Deux semaine avant"),
        ],
        label="Publication",
    )
    days = forms.MultipleChoiceField(
        choices=Event.DAYS,
        widget=forms.CheckboxSelectMultiple(),
        label="Jour(s) de récurrence",
    )
    hour = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        label="Heure de récurrence",
    )
    weeks = forms.MultipleChoiceField(
        choices=Event.WEEKS,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "for-month"}),
        label="La ou les semaines de récurrence",
        required=False,
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        label="La date de fin de la récurrence",
    )

    def clean_weeks(self):
        recurrent_type = self.cleaned_data["recurrent_type"]
        error_message = (
            "Vous devez renseigner au moins une semaine de récurrence."
        )
        if recurrent_type == "month":
            if not self.cleaned_data["weeks"]:
                self.add_error("weeks", error_message)

    # def save(self, commit=False):

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
