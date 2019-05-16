from django.contrib import messages
from django.urls import reverse_lazy

from django.views.generic import (
    DetailView,
    TemplateView,
    DeleteView,
    CreateView,
    UpdateView,
)

from ateliersoude.location.forms import PlaceForm
from ateliersoude.location.models import Place
from ateliersoude.user.mixins import IsAdminMixin
from ateliersoude.mixins import RedirectQueryParamView, PermissionMixin


class PlaceView(IsAdminMixin, DetailView):
    model = Place


class PlaceDeleteView(PermissionMixin, RedirectQueryParamView, DeleteView):
    model = Place
    success_url = reverse_lazy("location:list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Le lieu a bien été supprimé")
        return super().delete(request, *args, **kwargs)


class PlaceMapView(TemplateView):
    template_name = "location/place_list.html"


class PlaceFormView(PermissionMixin):
    def form_valid(self, form):
        validated = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return validated


class PlaceCreateView(RedirectQueryParamView, PlaceFormView, CreateView):
    form_class = PlaceForm
    model = Place
    success_message = "Le lieu a bien été créé"


class PlaceEditView(RedirectQueryParamView, PlaceFormView, UpdateView):
    form_class = PlaceForm
    model = Place
    success_message = "Le lieu a bien été modifié"
