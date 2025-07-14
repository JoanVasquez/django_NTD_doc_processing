# 🌐 URL Configuration for doc_processor project

from __future__ import annotations

from django.shortcuts import redirect
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# 📚 Swagger Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Document Processor API",
        default_version='v1',
        description="OCR, document classification, and entity extraction API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# 📌 URL Patterns
urlpatterns = [
    # 🏠 Root redirect to Swagger
    path('', lambda request: redirect('schema-swagger-ui')),
    # 📡 API Routes
    path('api/', include('api.urls')),
    # 📚 API Documentation
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
