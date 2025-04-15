# apps/documents/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.documents.models import QRCode, Dossier, Fichier
from apps.documents.serializers import QRCodeSerializer, DossierSerializer, FichierSerializer

class QRCodeViewSet(viewsets.ModelViewSet):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]


class DossierViewSet(viewsets.ModelViewSet):
    queryset = Dossier.objects.all()
    serializer_class = DossierSerializer
    permission_classes = [IsAuthenticated]


class FichierViewSet(viewsets.ModelViewSet):
    queryset = Fichier.objects.all()
    serializer_class = FichierSerializer
    permission_classes = [IsAuthenticated]

