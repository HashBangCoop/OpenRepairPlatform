from django.contrib import admin

from .models import Activity, Condition, Event


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "activity",
        "organization",
        "published",
        "starts_at",
        "available_seats",
        "location",
        "slug",
    )
    ordering = ("-starts_at",)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ConditionAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(Event, EventAdmin)
admin.site.register(Condition, ConditionAdmin)
admin.site.register(Activity, ActivityAdmin)
