from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from ateliersoude.user.models import Organization


class PermissionOrganizationMixin:
    organization = None

    def get(self, request, *args, **kwargs):
        self._set_orga_from_kwargs(kwargs, request.user)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._set_orga_from_kwargs(kwargs, request.user)
        return super().post(request, *args, **kwargs)

    def _set_orga_from_kwargs(self, kwargs, user):
        orga_pk = kwargs["orga_pk"]
        orga = get_object_or_404(Organization, pk=orga_pk)
        self.organization = orga
        if user not in self.get_authorized_users():
            raise PermissionDenied(
                "Vous n'avez pas les droits pour gérer cette association"
            )


class PermissionAdminOrganizationMixin(PermissionOrganizationMixin):
    def get_authorized_users(self):
        return self.organization.admins.all()


class PermissionVolunteerOrganizationMixin(PermissionOrganizationMixin):
    def get_authorized_users(self):
        return self.organization.volunteers.union(
            self.organization.admins.all()
        )
