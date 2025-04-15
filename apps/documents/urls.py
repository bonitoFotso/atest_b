# apps/documents/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.documents.views import QRCodeViewSet, DossierViewSet, FichierViewSet

router = DefaultRouter()
router.register(r'qrcodes', QRCodeViewSet)
router.register(r'dossiers', DossierViewSet)
router.register(r'fichiers', FichierViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
