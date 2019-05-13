from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    RedirectView,
)

from ateliersoude.event.mixins import PermissionAdminOrganizationMixin
from ateliersoude.event.models import Event
from ateliersoude.event.templatetags.app_filters import tokenize
from ateliersoude.user.models import CustomUser, Organization
from ateliersoude.utils import get_future_published_events

from .forms import (
    UserUpdateForm,
    UserCreateForm,
    OrganizationForm,
    CustomUserEmailForm,
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
    form_class = CustomUserEmailForm

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
        context["register_form"] = CustomUserEmailForm
        context["add_admin_form"] = CustomUserEmailForm(auto_id="id_admin_%s")
        context["add_volunteer_form"] = CustomUserEmailForm(
            auto_id="id_volunteer_%s"
        )
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


class AddUserToOrganization(PermissionAdminOrganizationMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        email = self.request.POST.get("email", "")
        user = (
            CustomUser.objects.filter(email=email).exclude(password="").first()
        )
        redirect_url = reverse(
            "user:organization_detail",
            kwargs={
                "pk": self.organization.pk,
                "slug": self.organization.slug,
            },
        )

        if not user:
            messages.error(
                self.request,
                "L'utilisateur avec l'email " f"'{email}' n'existe pas",
            )
            return redirect_url

        if user in self.organization.admins.all():
            messages.warning(
                self.request,
                "Action impossible: l'utilisateur fait déjà partie des admins "
                "de l'association"
            )
            return redirect_url

        self.add_user_to_orga(self.organization, user)
        messages.success(self.request, f"Bienvenue {user.first_name}!")
        return redirect_url


class AddAdminToOrganization(AddUserToOrganization):
    @staticmethod
    def add_user_to_orga(orga, user):
        orga.volunteers.remove(user)
        orga.admins.add(user)


class AddVolunteerToOrganization(AddUserToOrganization):
    @staticmethod
    def add_user_to_orga(orga, user):
        orga.volunteers.add(user)


class RemoveUserFromOrganization(
    PermissionAdminOrganizationMixin, RedirectView
):
    def get_redirect_url(self, *args, **kwargs):
        user_pk = kwargs["user_pk"]
        user = get_object_or_404(CustomUser, pk=user_pk)
        self.remove_user_from_orga(self.organization, user)
        messages.success(
            self.request,
            f"L'utilisateur {user.first_name} " "a bien été retiré !",
        )

        return reverse(
            "user:organization_detail",
            kwargs={
                "pk": self.organization.pk,
                "slug": self.organization.slug,
            },
        )


class RemoveAdminFromOrganization(RemoveUserFromOrganization):
    @staticmethod
    def remove_user_from_orga(orga, user):
        orga.admins.remove(user)


class RemoveVolunteerFromOrganization(RemoveUserFromOrganization):
    @staticmethod
    def remove_user_from_orga(orga, user):
        orga.volunteers.remove(user)
