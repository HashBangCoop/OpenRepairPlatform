from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, ListView

from ateliersoude.plateformeweb.models import Event

from .forms import CustomUserCreationForm, UserForm
from .models import CustomUser

from fm.views import AjaxCreateView, AjaxUpdateView
from logging import getLogger

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)

from django.core.mail import send_mail

from ateliersoude.users.models import CustomUser
from .models import (
    Activity,
    Condition,
    Event,
    Organization,
    OrganizationPerson,
    Place,
)


def user_profile(request):
    if request.method == "GET":
        return render(request,
                      "users/user_profile.html",
                      {"user_form": UserForm(instance=request.user,
                                             label_suffix="",
                                             auto_id="field_id_%")},
                      )

    else:
        user_form = UserForm(
            request.POST, instance=CustomUser.objects.get(id=request.user.id)
        )
        if user_form.is_valid():
            user_form.save()
            action.send(request.user, verb="a modifié ses informations")
        return render(request,
                      "users/user_profile.html",
                      {"user_form": user_form})


def list_users(request):
    if request.method == "GET":
        return render(request,
                      "users/user_profile.html",
                      {"user_form": UserForm(instance=request.user,
                                             label_suffix="",
                                             auto_id="field_id_%")},
                      )
    else:
        return


# doc :
# https://stackoverflow.com/questions/26347725/django-custom-user-creation-form


def register(request):

    form = CustomUserCreationForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            form.save()
            new_user = authenticate(
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
            )
            login(request, new_user)
            return HttpResponseRedirect(reverse("user_profile"))

    return render(request, "users/user_create.html", {"form": form})


class UserDetailView(DetailView):
    model = CustomUser
    context_object_name = "target_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['attending_events'] = Event.objects.all()
        user = context["target_user"]
        attendees = Event.objects.filter(attendees=user)
        context["attending_events"] = attendees
        return context


class UserListView(ListView):
    model = CustomUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "user"
        return context


class OrganizationView(DetailView):
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OrganizationListView(ListView):
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "organization"
        return context


# --- edit ---


class OrganizationFormView:
    model = Organization
    fields = ["name", "description", "picture", "active"]

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        form.fields["description"] = forms.CharField()
        return form

    def get_success_url(self):
        return reverse_lazy(
            "organization_detail", args=(self.object.pk, self.object.slug)
        )


class OrganizationCreateView(OrganizationFormView, CreateView):
    permission_required = "plateformeweb.create_organization"


class OrganizationEditView(OrganizationFormView, AjaxUpdateView):
    # permission_required = 'plateformeweb.edit_organization'
    queryset = Organization.objects


# -- Admin page to manage the organization contents --


def OrganizationManager(request, pk):
    organization = Organization.objects.get(pk=pk)
    organization_admins = organization.admins()
    if request.user in organization_admins:
        context = {"organization": organization}
    return render(request, "plateformeweb/organization_manager.html", context)


