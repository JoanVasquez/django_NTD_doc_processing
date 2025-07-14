from __future__ import annotations

from typing import List
from django.urls import path, URLPattern
from api.views import DocumentProcessView

urlpatterns = [
    path('process-document/', DocumentProcessView.as_view(), name='process_document'),
]
