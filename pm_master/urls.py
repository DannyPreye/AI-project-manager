from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Project Manager API",
        default_version='v1',
        description="AI-powered project management system with Trello integration",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@projectmanager.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,

)

api_path="api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{api_path}organization/", include("organization.urls")),
    path(f"{api_path}project/", include("project.urls")),

    # path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
