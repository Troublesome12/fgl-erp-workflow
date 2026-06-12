"""Root URL configuration including health check, API mount, and OpenAPI docs."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from workflow.views import HealthView

urlpatterns = [
    path("health", HealthView.as_view()),
    path("api/", include("workflow.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
