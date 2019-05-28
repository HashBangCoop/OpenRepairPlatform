class PermissionOrgaContextMixin:
    """
    Adds two context variables: `is_admin` and `is_volunteer`
    telling us which information the current user can see in templates
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.object, "organization"):
            organization = self.object.organization
        else:
            organization = self.object
        user = self.request.user
        context["is_admin"] = (
            user.is_authenticated and user in organization.admins.all()
        )
        context["is_volunteer"] = (
            user.is_authenticated
            and user in organization.volunteers.all()
            or user in organization.actives.all()
            or context["is_admin"]
        )
        return context
