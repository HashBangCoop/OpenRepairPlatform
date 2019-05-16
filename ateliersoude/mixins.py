from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import Resolver404, resolve
from django.shortcuts import get_object_or_404
from ateliersoude.user.models import Organization


def is_valid_path(path: str) -> bool:
    if not isinstance(path, str):
        return False
    try:
        # this call throws if the redirect is not registered in urls.py
        resolve(path)
        return True
    except Resolver404:
        return False


class RedirectQueryParamView:
    def get_success_url(self):
        redirect = self.request.GET.get("redirect")
        default_redirect = super().get_success_url()
        if is_valid_path(redirect):
            return redirect
        else:
            return default_redirect


class PermissionMixin(PermissionRequiredMixin):
    organization = None
    permission_denied_message = (
        "Vous n'êtes pas administrateur de l'organisation."
    )

    def get_organization_admins(self):
        orga_pk = self.kwargs.get("orga_pk")
        if orga_pk:
            orga = get_object_or_404(Organization, pk=orga_pk)
        else:
            orga = get_object_or_404(
                self.model, pk=self.kwargs.get("pk")
            ).organization
        self.organization = orga
        return orga.admins.all()

    def has_permission(self):
        if self.request.user not in self.get_organization_admins():
            return False
        return True
