import logging

from django.contrib import messages
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    RedirectView,
    FormView,
)

from ateliersoude import utils
from ateliersoude.event.forms import (
    EventForm,
    ActivityForm,
    ConditionForm,
    EventSearchForm,
    RecurrentEventForm,
)
from ateliersoude.event.models import Activity, Condition, Event
from ateliersoude.event.templatetags.app_filters import tokenize
from ateliersoude.mixins import (
    RedirectQueryParamView,
    HasAdminPermissionMixin,
    HasVolunteerPermissionMixin,
)
from ateliersoude.user.mixins import PermissionOrgaContextMixin
from ateliersoude.user.forms import CustomUserEmailForm, MoreInfoCustomUserForm
from ateliersoude.user.models import CustomUser

logger = logging.getLogger(__name__)


class ConditionFormView(HasAdminPermissionMixin):
    model = Condition
    form_class = ConditionForm
    template_name = "event/condition/form.html"

    def form_valid(self, form):
        form.instance.organization = self.organization
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        orga = self.object.organization
        return reverse("user:organization_detail", args=[orga.pk, orga.slug])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["organization"] = self.organization
        return ctx


class ConditionCreateView(
    RedirectQueryParamView, ConditionFormView, CreateView
):
    success_message = "La Condition a bien été créée"


class ConditionEditView(RedirectQueryParamView, ConditionFormView, UpdateView):
    success_message = "La Condition a bien été mise à jour"


class ConditionDeleteView(HasAdminPermissionMixin, DeleteView):
    model = Condition
    template_name = "event/condition/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "La condition a bien été supprimée")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()


class ActivityView(PermissionOrgaContextMixin, DetailView):
    model = Activity
    template_name = "event/activity/detail.html"


class ActivityListView(ListView):
    model = Activity
    template_name = "event/activity/list.html"


class ActivityFormView(HasAdminPermissionMixin):
    model = Activity
    form_class = ActivityForm
    template_name = "event/activity/form.html"

    def form_valid(self, form):
        form.instance.organization = self.organization
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ActivityCreateView(RedirectQueryParamView, ActivityFormView, CreateView):
    success_message = "L'activité a bien été créée"


class ActivityEditView(RedirectQueryParamView, ActivityFormView, UpdateView):
    success_message = "L'activité a bien été mise à jour"


class ActivityDeleteView(
    HasAdminPermissionMixin, RedirectQueryParamView, DeleteView
):
    model = Activity
    success_url = reverse_lazy("event:activity_list")
    template_name = "event/activity/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "L'activité a bien été supprimée")
        return super().delete(request, *args, **kwargs)


class EventView(PermissionOrgaContextMixin, DetailView):
    model = Event
    template_name = "event/event_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["register_form"] = CustomUserEmailForm
        ctx["present_form"] = MoreInfoCustomUserForm
        return ctx


class EventListView(ListView):
    model = Event
    template_name = "event/event_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = EventSearchForm(self.request.GET)
        context["register_form"] = CustomUserEmailForm
        return context

    def get_queryset(self):
        queryset = Event.future_published_events()
        form = EventSearchForm(self.request.GET)
        if not form.is_valid():
            return queryset
        if form.cleaned_data["place"]:
            queryset = queryset.filter(location=form.cleaned_data["place"])
        if form.cleaned_data["organization"]:
            queryset = queryset.filter(
                organization=form.cleaned_data["organization"]
            )
        if form.cleaned_data["activity"]:
            queryset = queryset.filter(activity=form.cleaned_data["activity"])
        if form.cleaned_data["starts_before"]:
            queryset = queryset.filter(
                date__lte=form.cleaned_data["starts_before"]
            )
        if form.cleaned_data["starts_after"]:
            queryset = queryset.filter(
                date__gte=form.cleaned_data["starts_after"]
            )
        return queryset


class EventFormView(HasAdminPermissionMixin):
    model = Event
    form_class = EventForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"orga": self.organization})
        return kwargs

    def form_valid(self, form):
        form.instance.organization = self.organization
        event = form.save()
        event.organizers.add(self.request.user)
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(event.get_absolute_url())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orga"] = self.organization
        return ctx


class EventEditView(RedirectQueryParamView, EventFormView, UpdateView):
    success_message = "L'évènement a bien été modifié"


class EventCreateView(RedirectQueryParamView, EventFormView, CreateView):
    success_message = "L'évènement a bien été créé"


class EventDeleteView(
    HasAdminPermissionMixin, RedirectQueryParamView, DeleteView
):
    model = Event
    success_url = reverse_lazy("event:list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "L'évènement a bien été supprimé")
        return super().delete(request, *args, **kwargs)


class RecurrentEventCreateView(HasAdminPermissionMixin, FormView):
    form_class = RecurrentEventForm
    success_url = reverse_lazy("event:list")
    template_name = "event/recurrent_event_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"orga": self.organization})
        return kwargs

    def form_valid(self, form):
        res = super().form_valid(form)
        count = form.save()
        messages.success(
            self.request, f"Vous avez créé {count} événements récurrents"
        )
        return res

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orga"] = self.organization
        return ctx


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
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")

        event.registered.remove(user)
        event.presents.add(user)
        messages.success(self.request, f"{user} est présent !")

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
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")

        event.registered.add(user)
        event.presents.remove(user)
        messages.success(self.request, f"{user} a été marqué comme absent !")

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
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")

        event.registered.remove(user)

        event_url = reverse("event:detail", args=[event.id, event.slug])
        event_url = self.request.build_absolute_uri(event_url)

        if user.first_name == "":
            # This is a temporary user created only for this event, we can
            # delete it
            user.delete()
        else:
            book_token = tokenize(user, event, "book")
            book_url = reverse("event:book", args=[book_token])
            book_url = self.request.build_absolute_uri(book_url)

        msg_plain = render_to_string("event/mail/unbook.txt", context=locals())
        msg_html = render_to_string("event/mail/unbook.html", context=locals())

        date = event.date.strftime("%d %B")
        subject = (
            f"Confirmation d'annulation pour le "
            f"{date} à {event.location.name}"
        )

        send_mail(
            subject,
            msg_plain,
            "no-reply@atelier-soude.fr",
            [user.email],
            html_message=msg_html,
        )

        messages.success(
            self.request, "Vous n'êtes plus inscrit à cet évènement"
        )

        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug])


class BookView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        token = kwargs["token"]
        try:
            event, user = _load_token(token, "book")
        except Exception:
            logger.exception(f"Error loading token {token} during book")
            messages.error(
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")

        event.registered.add(user)

        unbook_token = tokenize(user, event, "cancel")
        cancel_url = reverse("event:cancel_reservation", args=[unbook_token])
        cancel_url = self.request.build_absolute_uri(cancel_url)
        register_url = reverse("user:user_create")
        register_url = self.request.build_absolute_uri(register_url)

        event_url = reverse("event:detail", args=[event.id, event.slug])
        event_url = self.request.build_absolute_uri(event_url)

        msg_plain = render_to_string("event/mail/book.txt", context=locals())
        msg_html = render_to_string("event/mail/book.html", context=locals())

        date = event.date.strftime("%d %B")
        subject = f"Votre réservation du {date} à {event.location.name}"

        send_mail(
            subject,
            msg_plain,
            "no-reply@atelier-soude.fr",
            [user.email],
            html_message=msg_html,
        )

        messages.success(
            self.request, "Vous êtes inscrit à cet évènement, à bientôt !"
        )

        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug])


class CloseEventView(HasVolunteerPermissionMixin, RedirectView):
    http_method_names = ["post"]
    model = Event

    def get_redirect_url(self, *args, **kwargs):
        event_pk = kwargs["pk"]
        event = get_object_or_404(Event, pk=event_pk)
        for temp_user in event.registered.filter(first_name=""):
            temp_user.delete()
        for present in event.presents.all():
            if present.first_name == "":
                event.organization.visitors.add(present)
            else:
                event.organization.members.add(present)

        messages.success(self.request, "L'évènement a été clôturé avec succès")

        return reverse("event:detail", args=[event.id, event.slug])
