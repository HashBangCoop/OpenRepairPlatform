from fm.views import AjaxCreateView, AjaxUpdateView

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    ListView,
)

from ateliersoude.location.models import Place


class PlaceView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PlaceListView(ListView):
    model = Place

    def get_context_data(self, **kwargs):
        context = {"list_type": "place"}
        return context


class PlaceFormView:

    model = Place
    fields = [
        "name",
        "description",
        "type",
        "address",
        "picture",
        "organization"]

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        form.fields["description"] = forms.CharField()
        return form

    def get_success_url(self):
        return reverse_lazy(
            "place_detail", args=(
                self.object.pk, self.object.slug))


class PlaceCreateView(PlaceFormView, AjaxCreateView):
    # permission_required = 'plateformeweb.create_place'

    def validate_image(self, image):
        # Asserts image is smaller than 5MB
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("L'image est trop lourde (> 5Mo)")
            return image
        else:
            raise ValidationError("Erreur dans le téléversement du fichier")

    # set owner to current user on creation
    def form_valid(self, form):
        image = form.cleaned_data.get("picture", False)
        self.validate_image(image)
        obj = form.save()
        obj.owner = self.request.user
        # Make messages django for information : "'user' a créé" Place
        return super().form_valid(form)


class PlaceEditView(PlaceFormView, AjaxUpdateView):
    # permission_required = 'plateformeweb.edit_place'
    queryset = Place.objects

    def validate_image(self, image):
        # Asserts image is smaller than 5MB
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("L'image est trop lourde (> 5Mo)")
            return image
        else:
            raise ValidationError("Erreur dans le téléversement du fichier")

    def form_valid(self, form):
        image = form.cleaned_data.get("picture", False)
        self.validate_image(image)
        form.save(commit=False)
        # Make messages django for information : "'user' a modifié" Place
        return super().form_valid(form)
