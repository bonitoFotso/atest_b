from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Client, Affaire, Statut
from .serializers import (
    ClientCreateSerializer,
    ClientListSerializer,
    ClientDetailSerializer,
    AffaireCreateSerializer,
    AffaireListSerializer,
    AffaireDetailSerializer,
    StatutSerializer
)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        elif self.action == 'retrieve':
            return ClientDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ClientCreateSerializer
        return ClientDetailSerializer

class AffaireViewSet(viewsets.ModelViewSet):
    queryset = Affaire.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return AffaireListSerializer
        elif self.action == 'retrieve':
            return AffaireDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AffaireCreateSerializer
        return AffaireDetailSerializer

class StatutViewSet(viewsets.ModelViewSet):
    queryset = Statut.objects.all()
    serializer_class = StatutSerializer
    permission_classes = [IsAuthenticated]
