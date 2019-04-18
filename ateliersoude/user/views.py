from django import forms
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from ateliersoude.event.models import Event
from ateliersoude.user.models import CustomUser, Organization

from .forms import CustomUserCreationForm, UserForm


def user_profile(request):
    if request.method == "GET":
        return render(
            request,
            "user/user_profile.html",
            {
                "user_form": UserForm(
                    instance=request.user,
                    label_suffix="",
                    auto_id="field_id_%",
                )
            },
        )

    else:
        user_form = UserForm(
            request.POST, instance=CustomUser.objects.get(id=request.user.id)
        )
        if user_form.is_valid():
            user_form.save()
            # action.send(request.user, verb="a modifié ses informations")
        return render(
            request, "user/user_profile.html", {"user_form": user_form}
        )


def list_users(request):
    if request.method == "GET":
        return render(
            request,
            "user/user_profile.html",
            {
                "user_form": UserForm(
                    instance=request.user,
                    label_suffix="",
                    auto_id="field_id_%",
                )
            },
        )
    else:
        return


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

    return render(request, "user/user_create.html", {"form": form})


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
    template_name = "user/organisation/organization_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OrganizationListView(ListView):
    model = Organization
    template_name = "user/organisation/organization_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "organization"
        return context


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


class OrganizationEditView(OrganizationFormView, UpdateView):
    # permission_required = 'plateformeweb.edit_organization'
    queryset = Organization.objects


# -- Admin page to manage the organization contents --


def OrganizationManager(request, pk):
    organization = Organization.objects.get(pk=pk)
    organization_admins = organization.admins()
    if request.user in organization_admins:
        context = {"organization": organization}
    return render(
        request, "user/organisation/organization_manager.html", context
    )
