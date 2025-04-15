from django.shortcuts import redirect, get_object_or_404
from rest_framework import generics
from file_api.models import Client, Site, InspectionType, Rapport, Dossier, Fichier, Etiquette
from .serializers import (
    ClientSerializer, SiteSerializer, InspectionTypeSerializer, RapportSerializer,
    RapportCreateSerializer,
    RapportListSerializer
)


# Client CRUD
class ClientListCreateAPIView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


# Site CRUD with parent Client context
class ClientSiteListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SiteSerializer

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Site.objects.filter(client_id=client_id)

    def perform_create(self, serializer):
        client_id = self.kwargs['client_id']
        client = Client.objects.get(pk=client_id)
        serializer.save(client=client)


class SiteListCreateAPIView(generics.ListCreateAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class SiteRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


# InspectionType CRUD
class InspectionTypeListCreateAPIView(generics.ListCreateAPIView):
    queryset = InspectionType.objects.all()
    serializer_class = InspectionTypeSerializer


class InspectionTypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InspectionType.objects.all()
    serializer_class = InspectionTypeSerializer


# Rapport CRUD
class RapportListCreateView(generics.ListCreateAPIView):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer


class RapportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer


class RapportCreateView(generics.CreateAPIView):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer

    def perform_create(self, serializer):
        rapport = serializer.save()

        # Construire la hiérarchie des dossiers
        annee = rapport.date_inspection.year
        client = rapport.site.client
        site = rapport.site
        inspectionType = rapport.inspectionType
        etiquette_id = rapport.etiquette.id
        etiquette = Etiquette.objects.get(pk=etiquette_id)

        etiquette.isAssigned = True
        etiquette.save()



        # Créer ou obtenir les dossiers
        dossier_annee, _ = Dossier.objects.get_or_create(name=str(annee), parent=None)
        dossier_rapports, _ = Dossier.objects.get_or_create(name='rapports', parent=dossier_annee)
        dossier_client, _ = Dossier.objects.get_or_create(name=client.name, parent=dossier_rapports)
        dossier_site, _ = Dossier.objects.get_or_create(name=site.name, parent=dossier_client)
        dossier_type_inspection, _ = Dossier.objects.get_or_create(name=inspectionType.name, parent=dossier_site)
        dossier_numero_rapport, _ = Dossier.objects.get_or_create(name=rapport.numero_rapport, parent=dossier_type_inspection)
        fichier_rapport, _ = Fichier.objects.get_or_create(name=rapport.numero_rapport, dossier=dossier_numero_rapport,
                                                           fichier=rapport.fichier,
                                                           type='Rapport')
        fichier_etiquette, _ = Fichier.objects.get_or_create(name=etiquette.numero, dossier=dossier_numero_rapport,
                                                             fichier=etiquette.image,
                                                             type='Etiquette'
                                                             )
        fichiet_qr_code, _ = Fichier.objects.get_or_create(name=etiquette.qrcode.code,
                                                           dossier=dossier_numero_rapport,
                                                           fichier=etiquette.qrcode.image,
                                                           type='QRCode'
                                                           )

        # Assigner le dossier au rapport
        rapport.dossier = dossier_type_inspection
        rapport.save()
