from django.contrib import admin

class PlaceTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "raw_address", "slug")

    def raw_address(self, obj):
        return obj.address.raw




admin.site.register(PlaceType, PlaceTypeAdmin)
admin.site.register(Place, PlaceAdmin)
