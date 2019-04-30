from django.contrib import admin

from .models import Activity, Condition, Event


admin.site.register(Event)
admin.site.register(Condition)
admin.site.register(Activity)
