import logging

from django.contrib import messages
from django.core import signing
from django.core.mail import send_mail
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseForbidden,
)
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    RedirectView,
)

from ateliersoude import utils
from ateliersoude.event.forms import EventForm, ActivityForm, ConditionForm
from ateliersoude.event.models import Activity, Condition, Event
from ateliersoude.mixins import RedirectQueryParamView
from ateliersoude.user.models import CustomUser, Organization

logger = logging.getLogger(__name__)


class ConditionFormView:
    model = Condition
    form_class = ConditionForm
    orga = None

    def get(self, request, *args, **kwargs):
        self._set_orga_from_kwargs(kwargs)
        if request.user not in self.orga.volunteers.union(
            self.orga.admins.all()
        ):
            return HttpResponseForbidden(
                "Vous ne pouvez pas créer de "
                "condition pour cette association"
            )
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._set_orga_from_kwargs(kwargs)
        if request.user not in self.orga.volunteers.union(
            self.orga.admins.all()
        ):
            return HttpResponseForbidden(
                "Vous ne pouvez pas créer de "
                "condition pour cette association"
            )
        return super().post(request, *args, **kwargs)

    def _set_orga_from_kwargs(self, kwargs):
        orga_pk = kwargs.pop("orga_pk")
        orga = get_object_or_404(Organization, pk=orga_pk)
        self.orga = orga

    def form_valid(self, form):
        form.instance.organization = self.orga
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        orga = self.object.organization
        return reverse("user:organization_detail", args=[orga.pk, orga.slug])


class ConditionCreateView(
    RedirectQueryParamView, ConditionFormView, CreateView
):
    success_message = "La Condition a bien été créée"


class ConditionEditView(RedirectQueryParamView, ConditionFormView, UpdateView):
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
    orga = None

    def get(self, request, *args, **kwargs):
        self._set_orga_from_kwargs(kwargs)
        if request.user not in self.orga.volunteers.union(
            self.orga.admins.all()
        ):
            return HttpResponseForbidden(
                "Vous ne pouvez pas créer d'activité " "pour cette association"
            )
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._set_orga_from_kwargs(kwargs)
        if request.user not in self.orga.volunteers.union(
            self.orga.admins.all()
        ):
            return HttpResponseForbidden(
                "Vous ne pouvez pas créer d'activité " "pour cette association"
            )
        return super().post(request, *args, **kwargs)

    def _set_orga_from_kwargs(self, kwargs):
        orga_pk = kwargs.pop("orga_pk")
        orga = get_object_or_404(Organization, pk=orga_pk)
        self.orga = orga

    def form_valid(self, form):
        form.instance.organization = self.orga
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ActivityCreateView(RedirectQueryParamView, ActivityFormView, CreateView):
    model = Activity
    form_class = ActivityForm
    success_message = "L'activité a bien été créée"


class ActivityEditView(RedirectQueryParamView, ActivityFormView, UpdateView):
    model = Activity
    form_class = ActivityForm
    success_message = "L'activité a bien été mise à jour"


class ActivityDeleteView(RedirectQueryParamView, DeleteView):
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

    def get_queryset(self):
        return Event.future_published_events()


class EventFormView:
    orga = None

    def get(self, request, *args, **kwargs):
        self._set_orga_from_kwargs(kwargs)
        if request.user not in self.orga.volunteers.union(
            self.orga.admins.all()
        ):
            return HttpResponseForbidden(
                "Vous ne pouvez pas créer d'évènement"
                " pour cette association"
            )
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._set_orga_from_kwargs(kwargs)
        if request.user not in self.orga.volunteers.union(
            self.orga.admins.all()
        ):
            return HttpResponseForbidden(
                "Vous ne pouvez pas créer d'évènement"
                " pour cette association"
            )
        return super().post(request, *args, **kwargs)

    def _set_orga_from_kwargs(self, kwargs):
        orga_pk = kwargs.pop("orga_pk")
        orga = get_object_or_404(Organization, pk=orga_pk)
        self.orga = orga

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"orga": self.orga})
        return kwargs

    def form_valid(self, form):
        form.instance.organization = self.orga
        event = form.save()
        event.organizers.add(self.request.user)
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(event.get_absolute_url())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orga"] = self.orga
        return ctx


class EventEditView(RedirectQueryParamView, EventFormView, UpdateView):
    model = Event
    form_class = EventForm
    success_message = "L'évènement a bien été modifié"


class EventCreateView(RedirectQueryParamView, EventFormView, CreateView):
    model = Event
    form_class = EventForm
    success_message = "L'évènement a bien été créé"


class EventDeleteView(RedirectQueryParamView, DeleteView):
    model = Event
    success_url = reverse_lazy("event:list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "L'évènement a bien été supprimé")
        return super().delete(request, *args, **kwargs)


def _load_token(token, salt):
    ret = signing.loads(token, salt=salt)
    event_id = ret["event_id"]
    user_id = ret["user_id"]
    return Event.objects.get(pk=event_id), CustomUser.objects.get(pk=user_id)


class PresentView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        token = kwargs["token"]
        try:
            event, user = _load_token(token, "present")
        except Exception:
            logger.exception(f"Error loading token {token} during present")
            messages.error(
                self.request,
                "Une erreur est survenue lors de " "votre requête",
            )
            return reverse("event:list")

        event.registered.remove(user)
        event.presents.add(user)

        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug])


class AbsentView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        token = kwargs["token"]
        try:
            event, user = _load_token(token, "absent")
        except Exception:
            logger.exception(f"Error loading token {token} during asbent")
            messages.error(
                self.request,
                "Une erreur est survenue lors de " "votre requête",
            )
            return reverse("event:list")

        event.presents.remove(user)
        event.registered.add(user)

        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug])


class CancelReservationView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        token = kwargs["token"]
        try:
            event, user = _load_token(token, "cancel")
        except Exception:
            logger.exception(f"Error loading token {token} during unbook")
            messages.error(
                self.request,
                "Une erreur est survenue lors de " "votre requête",
            )
            return reverse("event:list")

        event.registered.remove(user)
        event.save()
        # TODO send email
        messages.success(
            self.request, "Vous n'êtes plus inscrit à cet " "évènement"
        )

        # TODO if id_user in present -> ???

        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug])


class BookView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # TODO: change with email, if not `user`, create one with email
        token = kwargs["token"]
        try:
            event, user = _load_token(token, "book")
        except Exception:
            logger.exception(f"Error loading token {token} during book")
            messages.error(
                self.request,
                "Une erreur est survenue lors de " "votre requête",
            )
            return reverse("event:list")

        event.registered.add(user)
        # TODO send email
        messages.success(
            self.request, "Vous êtes inscrit à cet évènement, " "à bientôt !"
        )

        # TODO if id_user in present -> ???

        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug])


# Following lines not used for now


def send_booking_mail(request, user, event):
    user_id = user.id
    event_id = event.id

    data = {"event_id": event_id, "user_id": user_id}

    cancel_token = signing.dumps(data)
    cancel_url = reverse("cancel_reservation", args=[cancel_token])
    cancel_url = request.build_absolute_uri(cancel_url)

    event_url = reverse("event_detail", args=[event_id, event.slug])
    event_url = request.build_absolute_uri(event_url)

    params = {"cancel_url": cancel_url, "event_url": event_url, "event": event}

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
