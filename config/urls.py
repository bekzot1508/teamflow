from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("", dashboard, name="dashboard"),
    path("", include("apps.users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)