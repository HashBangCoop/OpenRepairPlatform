from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.HomeView.as_view()),
    path('admin/', admin.site.urls),
    path("plateformeweb/", include("ateliersoude.plateformeweb.urls")),
    path("users/", include("ateliersoude.users.urls")),
    path("api/", include("ateliersoude.api.urls")),
]

# DEBUG toolbar if DEBUG is true in the environment
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
