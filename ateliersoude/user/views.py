from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)

from ateliersoude.event.models import Event
from ateliersoude.user.models import CustomUser, Organization
from .forms import (
    UserUpdateForm,
    UserCreateForm,
    OrganizationForm,
    AddUserToEventForm,
)


class UserUpdateView(UpdateView):
    model = CustomUser
    template_name = "user/user_profile.html"
    form_class = UserUpdateForm


class UserCreateView(CreateView):
    model = CustomUser
    template_name = "user/user_profile.html"
    form_class = UserCreateForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        res = super().form_valid(form)
        messages.success(self.request, "L'utilisateur a bien été créé.")
        return res


class UserDetailView(DetailView):
    model = CustomUser
    template_name = "user/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attending_events"] = Event.objects.filter(
            registered=self.object
        )
        return context


class UserListView(ListView):
    model = CustomUser
    template_name = "user/user_list.html"
    queryset = CustomUser.objects.filter(is_superuser=False)


class OrganizationDetailView(DetailView):
    model = Organization
    template_name = "user/organisation/organization_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["events"] = self.object.events.filter(
            published=True, starts_at__gt=timezone.now()
        )
        context["admin"] = (
            self.request.user.is_authenticated
            and self.request.user in self.object.admins.all()
            or self.request.user in self.object.volunteers.all()
        )
        context["form"] = AddUserToEventForm
        return context


class OrganizationListView(ListView):
    model = Organization
    template_name = "user/organisation/organization_list.html"


class OrganizationCreateView(CreateView):
    template_name = "user/organisation/organization_form.html"
    model = Organization
    form_class = OrganizationForm


class OrganizationUpdateView(UpdateView):
    template_name = "user/organisation/organization_form.html"
    model = Organization
    form_class = OrganizationForm


class OrganizationDeleteView(DeleteView):
    template_name = "user/organisation/confirmation_delete.html"
    model = Organization
    success_url = reverse_lazy("user:organization_list")

    def delete(self, request, *args, **kwargs):
        delete = super().delete(request, *args, **kwargs)
        messages.success(request, "Le lieu a bien été supprimé")
        return delete
