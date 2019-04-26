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


class PlaceView(DetailView):
    model = Place


class PlaceDeleteView(DeleteView):
    model = Place
    success_url = reverse_lazy("location:place_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Le lieu a bien été supprimé")
        return super().delete(request, *args, **kwargs)


class PlaceMapView(TemplateView):
    template_name = "location/place_list.html"


class PlaceFormView:
    def form_valid(self, form):
        validated = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return validated


class PlaceCreateView(PlaceFormView, CreateView):
    form_class = PlaceForm
    model = Place
    success_message = "Le lieu a bien été créé"


class PlaceEditView(PlaceFormView, UpdateView):
    form_class = PlaceForm
    model = Place
    success_message = "Le lieu a bien été modifié"
