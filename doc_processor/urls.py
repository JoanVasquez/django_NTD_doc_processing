# 🌐 URL Configuration for doc_processor project

from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Document Processor API",
        default_version='v1',
        description="A Django-based document processing system that performs OCR, document classification, and entity extraction using machine learning models and ChromaDB for vector storage.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@docprocessor.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# 📌 URL Patterns
urlpatterns = [
    # 📡 API Routes
    path('api/', include('api.urls')),
    # 📄 Swagger/OpenAPI Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Default to Swagger UI
]

