class IsAdminMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.object, "organization"):
            organization = self.object.organization
        else:
            organization = self.object
        user = self.request.user
        context["is_admin"] = (
            user.is_authenticated
            and user in organization.admins.all()
            or user.is_staff
        )
        context["is_volunteer"] = (
            user.is_authenticated
            and user in organization.volunteers.all()
            or context["is_admin"]
        )
        return context
