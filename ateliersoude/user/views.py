from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)

from ateliersoude.event.models import Event
from ateliersoude.event.templatetags.app_filters import tokenize
from ateliersoude.user.models import CustomUser, Organization
from ateliersoude.utils import get_future_published_events

from .forms import (
    UserUpdateForm,
    UserCreateForm,
    OrganizationForm,
    AddUserToEventForm,
)


class UserUpdateView(UpdateView):
    model = CustomUser
    template_name = "user/user_form.html"
    form_class = UserUpdateForm

    def form_valid(self, form):
        res = super().form_valid(form)
        messages.success(self.request, "L'utilisateur a bien été mis à jour.")
        return res


class UserCreateView(CreateView):
    model = CustomUser
    template_name = "user/user_form.html"
    form_class = UserCreateForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        res = super().form_valid(form)
        messages.success(self.request, "L'utilisateur a bien été créé.")
        return res


class UserCreateAndBookView(CreateView):
    model = CustomUser
    template_name = "user/user_form.html"
    form_class = AddUserToEventForm

    def post(self, request, *args, **kwargs):
        existing_user = CustomUser.objects.filter(
            email=request.POST.get("email", "invalid email")
        ).first()
        if existing_user:
            self.object = existing_user
            return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        event_id = self.request.GET.get("event")
        redirect_url = self.request.GET.get("redirect")
        event = get_object_or_404(Event, pk=event_id)
        token = tokenize(self.object, event, "book")
        return (
            reverse("event:book", kwargs={"token": token})
            + f"?redirect={redirect_url}"
        )


class UserDetailView(DetailView):
    model = CustomUser
    template_name = "user/user_detail.html"


class UserListView(ListView):
    model = CustomUser
    template_name = "user/user_list.html"
    queryset = CustomUser.objects.filter(is_superuser=False)


class OrganizationDetailView(DetailView):
    model = Organization
    template_name = "user/organization/organization_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["events"] = get_future_published_events(self.object.events)
        context["admin"] = (
            self.request.user.is_authenticated
            and self.request.user in self.object.admins.all()
            or self.request.user in self.object.volunteers.all()
        )
        context["form"] = AddUserToEventForm
        return context


class OrganizationListView(ListView):
    model = Organization
    template_name = "user/organization/organization_list.html"


class OrganizationCreateView(CreateView):
    template_name = "user/organization/organization_form.html"
    model = Organization
    form_class = OrganizationForm

    def form_valid(self, form):
        res = super().form_valid(form)
        # TODO : restriction user staff
        form.instance.admins.add(self.request.user)
        messages.success(self.request, "L'association a bien été créé.")
        return res


class OrganizationUpdateView(UpdateView):
    template_name = "user/organization/organization_form.html"
    model = Organization
    form_class = OrganizationForm

    def form_valid(self, form):
        res = super().form_valid(form)
        # TODO : restriction user staff
        messages.success(self.request, "L'association a bien été mise à jour.")
        return res


class OrganizationDeleteView(DeleteView):
    template_name = "user/organization/confirmation_delete.html"
    model = Organization
    success_url = reverse_lazy("user:organization_list")

    def delete(self, request, *args, **kwargs):
        delete = super().delete(request, *args, **kwargs)
        messages.success(request, "L'association a bien été supprimé")
        return delete
