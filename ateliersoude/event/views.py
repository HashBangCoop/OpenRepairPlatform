from django import forms
from django.contrib import messages
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)

from ateliersoude.event.forms import EventForm, ActivityForm, ConditionForm
from ateliersoude.event.models import Activity, Condition, Event
from ateliersoude.user.models import CustomUser, OrganizationPerson
from ateliersoude.utils import get_referer_resolver


class ConditionFormView:
    model = Condition
    form_class = ConditionForm

    def get_success_url(self):
        orga = self.object.organization
        return reverse("user:organization_detail", args=[orga.pk, orga.slug])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        print(form.fields["organization"].choices)
        # TODO: get orgas where user is admin
        # form.fields["organization"].choices = self.request.user.orga_admins
        return form

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ConditionCreateView(ConditionFormView, CreateView):
    success_message = "La Condition a bien été créée"


class ConditionEditView(ConditionFormView, UpdateView):
    success_message = "La Condition a bien été mise à jour"


class ConditionListView(ListView):
    model = Condition
    template_name = "event/condition_index.html"


class ConditionDeleteView(DeleteView):
    model = Condition

    def delete(self, request, *args, **kwargs):
        messages.success(request, "La condition a bien été supprimée")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()


class ActivityView(DetailView):
    model = Activity


class ActivityListView(ListView):
    model = Activity
    template_name = "event/activity_list.html"


class ActivityFormView:
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        print(form.fields["organization"].choices)
        # TODO: get orgas where user is admin
        # form.fields["organization"].choices = self.request.user.orga_admins
        return form

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ActivityCreateView(ActivityFormView, CreateView):
    model = Activity
    form_class = ActivityForm
    success_message = "L'activité a bien été créée"


class ActivityEditView(ActivityFormView, UpdateView):
    model = Activity
    form_class = ActivityForm
    success_message = "L'activité a bien été mise à jour"


class ActivityDeleteView(DeleteView):
    model = Activity
    success_url = reverse_lazy("event:activity_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "L'activité a bien été supprimée")
        return super().delete(request, *args, **kwargs)


class EventView(DetailView):
    model = Event
    template_name = "event/event_detail.html"


class EventListView(ListView):
    model = Event
    template_name = "event/event_list.html"
    queryset = Event.future_published_events()


class EventFormView:
    def form_valid(self, form):
        event = form.save()
        event.organizers.add(self.request.user)
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(event.get_absolute_url())


class EventEditView(EventFormView, UpdateView):
    model = Event
    form_class = EventForm
    success_message = "L'évènement a bien été modifié"


class EventCreateView(EventFormView, CreateView):
    model = Event
    form_class = EventForm
    success_message = "L'évènement a bien été créé"

    def get_initial(self):
        initial = super().get_initial()
        matched = get_referer_resolver(self.request)
        if not matched or matched.view_name != "user:organization_detail":
            return initial
        initial["organization"] = matched.kwargs.get("pk")
        return initial


class EventDeleteView(DeleteView):
    model = Event
    success_url = reverse_lazy("event:event_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "L'évènement a bien été supprimé")
        return super().delete(request, *args, **kwargs)


# Following lines are not used for now


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
