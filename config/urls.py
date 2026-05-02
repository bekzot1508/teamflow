from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from .views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),

    path("", include("apps.users.urls")),
    path("workspaces/", include("apps.workspaces.urls")),

    path("", include("apps.projects.urls")),
    path("", include("apps.tasks.urls")),

    path("notifications/", include("apps.notifications.urls")),

    path("__reload__/", include("django_browser_reload.urls")),

    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path("api/v1/workspaces/", include("apps.workspaces.api.urls")),
    path("api/v1/projects/", include("apps.projects.api.urls")),
    path("api/v1/tasks/", include("apps.tasks.api.urls")),
    path("api/v1/users/", include("apps.users.api.urls")),
    path("api/v1/notifications/", include("apps.notifications.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)