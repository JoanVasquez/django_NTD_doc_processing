from django.urls import path
from api.views import DocumentProcessView

urlpatterns = [
    path('process-document/', DocumentProcessView.as_view(), name='process_document'),
]
