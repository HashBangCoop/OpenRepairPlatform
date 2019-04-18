from django.contrib import messages
from django.urls import reverse_lazy

from django import forms
from django.views.generic import DetailView, TemplateView, DeleteView, \
    CreateView, UpdateView

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
    model = Place
    fields = [
        "name",
        "description",
        "place_type",
        "address",
        "picture",
        "organization",
        "longitude",
        "latitude",
    ]

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        form.fields["description"] = forms.CharField(widget=forms.Textarea)
        form.fields["longitude"] = forms.CharField(widget=forms.HiddenInput)
        form.fields["latitude"] = forms.CharField(widget=forms.HiddenInput)

        # Add bootstrap classes
        for field in form.fields.values():
            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_class} form-control"

        return form


class PlaceCreateView(PlaceFormView, CreateView):
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        messages.success(self.request, "Le lieu a bien été créé")
        return super().form_valid(form)


class PlaceEditView(PlaceFormView, UpdateView):
    def form_valid(self, form):
        obj = form.save()
        obj.owner = self.request.user
        messages.success(self.request, "Le lieu a bien été modifié")
        return super().form_valid(form)
