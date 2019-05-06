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
        orga_pk = kwargs.pop("orga_pk")
        orga = get_object_or_404(Organization, pk=orga_pk)
        self.organization = orga
        if user not in orga.volunteers.union(orga.admins.all()):
            raise PermissionDenied(
                "Vous ne pouvez pas créer de "
                f"`{self.object_kind}` pour cette association"
            )
