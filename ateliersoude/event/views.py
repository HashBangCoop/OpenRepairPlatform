import datetime

from django import forms
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from ateliersoude.event.models import Activity, Condition, Event
from ateliersoude.location.models import Place
from ateliersoude.user.models import (
    CustomUser,
    Organization,
    OrganizationPerson,
)


def send_notification(notification, activity):
    send_to = activity.participants.all()

    params = {"notification": notification}

    msg_plain = render_to_string("mail/notification.html", params)
    msg_html = render_to_string("mail/notification.html", params)

    subject = "nouvelle notification"

    for user in send_to:
        send_mail(
            subject,
            msg_plain,
            "no-reply@atelier-soude.fr",
            [user.email],
            html_message=msg_html,
        )


class ConditionView(DetailView):
    model = Condition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ConditionFormView:
    model = Condition
    fields = ["name", "resume", "description", "organization", "price"]

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)

        limited_choices = [["", "---------"]]
        form.fields["description"] = forms.CharField()
        user_orgs = OrganizationPerson.objects.filter(
            user=self.request.user, role__gte=OrganizationPerson.ADMIN
        )
        for result in user_orgs:
            organization = result.organization
            limited_choices.append([organization.pk, organization.name])
        form.fields["organization"].choices = limited_choices

        return form

    def get_success_url(self):
        return reverse_lazy(
            "activity_detail", args=(self.object.pk, self.object.slug)
        )


class ConditionCreateView(ConditionFormView, CreateView):
    # permission_required = 'plateformeweb.create_activity'

    # set owner to current user on creation
    def form_valid(self, form):
        return super().form_valid(form)


class ConditionEditView(ConditionFormView, UpdateView):
    # permission_required = 'plateformeweb.edit_acivity'
    queryset = Activity.objects


# --- Activity Types ---


class ActivityView(DetailView):
    model = Activity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ActivityListView(ListView):
    model = Activity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "activity"
        return context


class ActivityFormView:
    model = Activity
    fields = ["name", "description", "organization", "picture"]

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        form.fields["description"] = forms.CharField()

        limited_choices = [["", "---------"]]
        form.fields["description"] = forms.CharField()
        user_orgs = OrganizationPerson.objects.filter(
            user=self.request.user, role__gte=OrganizationPerson.ADMIN
        )
        for result in user_orgs:
            organization = result.organization
            limited_choices.append([organization.pk, organization.name])
        form.fields["organization"].choices = limited_choices

        return form

    def get_success_url(self):
        return reverse_lazy(
            "activity_detail", args=(self.object.pk, self.object.slug)
        )


class ActivityCreateView(ActivityFormView, CreateView):
    # permission_required = 'plateformeweb.create_activity'

    # set owner to current user on creation
    def form_valid(self, form):
        obj = form.save()
        obj.owner = self.request.user
        # Make messages django for information : "'user' a créé" Action
        notification = f"{obj.owner} a créé {obj}"
        send_notification(notification, activity=obj)
        return super().form_valid(form)


class ActivityEditView(ActivityFormView, UpdateView):
    # permission_required = 'plateformeweb.edit_acivity'
    queryset = Activity.objects

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        # Make messages django for information : "'user' a modifié" Action
        notification = f"{obj.owner} a modifié {obj}"
        send_notification(notification, activity=obj)
        return super().form_valid(form)


# --- Events ---


def cancel_reservation(request, token):
    ret = signing.loads(token)
    event_id = ret["event_id"]
    user_id = ret["user_id"]
    event = Event.objects.get(pk=event_id)
    user = CustomUser.objects.get(pk=user_id)
    context = {"event": event, "user": user}
    attendees = event.attendees.all()
    if user in attendees:
        event.attendees.remove(user)
        event.available_seats += 1
        event.save()
        return render(request, "mail/cancel_ok.html", context)
    else:
        return render(request, "mail/cancel_failed.html", context)


class EventView(DetailView):
    model = Event

    def get(self, request, **kwargs):
        event = Event.objects.get(pk=kwargs["pk"])
        confirmed = event.presents.all()
        for person in confirmed:
            event.attendees.remove(person)

        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = context["event"]
        context["event_id"] = event.id
        orga = event.organization
        admins = orga.admins()
        orga_volunteers = orga.volunteers()

        volunteers = []
        for v in orga_volunteers:
            if v in event.attendees.all():
                volunteers.append(v)

        context["admin_or_volunteer"] = admins + volunteers
        context["volunteers"] = volunteers
        context["admins"] = admins
        return context


class EventListView(ListView):
    queryset = {}

    def get(self, request, **kwargs):
        return render(request, "plateformeweb/event_list.html", {})

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     context["list_type"] = "event"
    #     return context


# --- edit ---


class EventEditView(UpdateView):
    permission_required = "plateformeweb.edit_event"
    fields = [
        "title",
        "type",
        "starts_at",
        "ends_at",
        "available_seats",
        "organizers",
        "location",
        "publish_at",
        "published",
        "organization",
        "condition",
    ]
    queryset = Event.objects


# --- booking form for current user ---


class BookingFormView:
    def send_booking_mail(self, user, event):
        user_id = user.id
        event_id = event.id

        data = {"event_id": event_id, "user_id": user_id}

        cancel_token = signing.dumps(data)
        cancel_url = reverse("cancel_reservation", args=[cancel_token])
        cancel_url = self.request.build_absolute_uri(cancel_url)

        event_url = reverse("event_detail", args=[event_id, event.slug])
        event_url = self.request.build_absolute_uri(event_url)

        params = {
            "cancel_url": cancel_url,
            "event_url": event_url,
            "event": event,
        }

        msg_plain = render_to_string("mail/relance.html", params)
        msg_html = render_to_string("mail/relance.html", params)

        date = event.starts_at.date().strftime("%d %B")
        location = event.location.name
        subject = "Votre réservation pour le " + date + " à " + location

        send_mail(
            subject,
            msg_plain,
            "no-reply@atelier-soude.fr",
            [user.email],
            html_message=msg_html,
        )


class BookingEditView(BookingFormView, UpdateView):

    template_name = "plateformeweb/booking_form.html"
    queryset = Event.objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = context["event"].id
        data = {"event_id": event_id}
        context["booking_id"] = signing.dumps(data)
        return context


# --- mass event ---


class EventCreateView(CreateView):
    # permission_required = 'plateformeweb.create_event'
    template_name = "plateformeweb/event_form.html"
    model = Event
    fields = [
        "type",
        "available_seats",
        "organization",
        "location",
        "condition",
        "starts_at",
        "ends_at",
        "publish_at",
    ]

    def date_substract(self, starts_at, countdown):
        # TODO: change this if haing a publish_date in the past is a problem
        return starts_at - datetime.timedelta(days=countdown)

    def post(self, request, *args, **kwargs):
        try:
            import simplejson as json
        except (ImportError,):
            import json

        json_data = request.POST["dates"]
        starts_at = request.POST["starts_at"]
        ends_at = request.POST["ends_at"]
        publish_countdown = int(request.POST["publish_at"])
        date_timestamps = json.loads(json_data)

        event_type = Activity.objects.get(pk=request.POST["type"])
        organization = Organization.objects.get(
            pk=request.POST["organization"]
        )
        available_seats = int(request.POST["available_seats"])
        location = Place.objects.get(pk=request.POST["location"])

        new_slug = str(event_type)
        new_slug += "-" + organization.slug
        new_slug += "-" + location.slug

        # today = timezone.now()

        for date in date_timestamps:
            starts_at = datetime.datetime.fromtimestamp(
                int(date + int(request.POST["starts_at"]))
            )
            ends_at = datetime.datetime.fromtimestamp(
                int(date + int(request.POST["ends_at"]))
            )
            publish_date = self.date_substract(starts_at, publish_countdown)

            e = Event.objects.create(
                organization=organization,
                slug=new_slug,
                owner=request.user,
                starts_at=starts_at,
                ends_at=ends_at,
                publish_at=publish_date,
                available_seats=available_seats,
                location=location,
                type=event_type,
            )

            e.organizers.add(CustomUser.objects.get(email=request.user.email))
            e.title = e.type.name
            e.save()
            # Make messages django for information : "'user' a créé" Event

        return HttpResponseRedirect(reverse("event_create"))

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        for field in ("starts_at", "ends_at", "publish_at"):
            form.fields[field].widget = forms.HiddenInput()

        limited_choices = [["", "---------"]]
        user_orgs = OrganizationPerson.objects.filter(
            user=self.request.user, role__gte=OrganizationPerson.ADMIN
        )

        for result in user_orgs:
            organization = result.organization
            limited_choices.append([organization.pk, organization.name])

        form.fields["organization"].choices = limited_choices
        # form.fields['organization'].queryset = user_orgs

        return form

    # set owner to current user on creation
    def form_valid(self, form):
        return super().form_valid(form)


class MassBookingCreateView(CreateView):
    template_name = "plateformeweb/mass_event_book.html"
    model = Event
    fields = []

    def post(self, request, *args, **kwargs):
        try:
            import simplejson as json
        except (ImportError,):
            import json

        json_data = request.POST["dates"]
        events_pk = json.loads(json_data)
        events_pk = list(map(int, events_pk))
        events = Event.objects.filter(pk__in=events_pk)
        # TODO: bulk insert somehow?
        for event in events:
            event.attendees.add(request.user)
        return HttpResponse("OK!")

    def get_form(self, form_class=None, **kwargs):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_success_url(self):
        return render(
            self.request,
            "plateformeweb/event_list.html",
            message="c'est tout bon",
        )
