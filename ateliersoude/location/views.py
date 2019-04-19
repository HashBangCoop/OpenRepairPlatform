from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.urls import reverse_lazy

from django.views.generic import DetailView, TemplateView, DeleteView, \
    CreateView, UpdateView

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


class PlaceCreateView(CreateView):
    form_class = PlaceForm
    model = Place

    def form_valid(self, form):
        obj = form.save(commit=False)
        try:
            obj.owner = self.request.user
        except ValueError:
            return HttpResponseBadRequest(
                "Impossible de créer un Lieu avec cet utilisateur".encode()
            )
        validated = super().form_valid(form)
        messages.success(self.request, "Le lieu a bien été créé")
        return validated


class PlaceEditView(UpdateView):
    form_class = PlaceForm
    model = Place

    def form_valid(self, form):
        obj = form.save(commit=False)
        try:
            obj.owner = self.request.user
        except ValueError:
            return HttpResponseBadRequest(
                "Impossible de mettre à jour ce Lieu avec cet "
                "utilisateur".encode()
            )
        validated = super().form_valid(form)
        messages.success(self.request, "Le lieu a bien été modifié")
        return validated
