
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated


from apps.documents.models import Dossier, Fichier
from apps.inspections.models import (
    InspectionType, LotEtiquette, Etiquette, Rapport, ArcFlashLabel
)
from apps.inspections.serializers import (
    InspectionTypeSerializer, LotEtiquetteSerializer, EtiquetteSerializer,
    RapportSerializer, ArcFlashLabelSerializer
)


class InspectionTypeViewSet(viewsets.ModelViewSet):
    queryset = InspectionType.objects.all()
    serializer_class = InspectionTypeSerializer
    permission_classes = [IsAuthenticated]


class LotEtiquetteViewSet(viewsets.ModelViewSet):
    queryset = LotEtiquette.objects.all()
    serializer_class = LotEtiquetteSerializer
    permission_classes = [IsAuthenticated]


class EtiquetteViewSet(viewsets.ModelViewSet):
    queryset = Etiquette.objects.all().order_by('-id')  # Assurez-vous que "id" est le nom du champ de date de création
    serializer_class = EtiquetteSerializer
    permission_classes = [IsAuthenticated]


class RapportViewSet(viewsets.ModelViewSet):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer
    permission_classes = [IsAuthenticated]

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



class ArcFlashLabelViewSet(viewsets.ModelViewSet):
    queryset = ArcFlashLabel.objects.all()
    serializer_class = ArcFlashLabelSerializer
    permission_classes = [IsAuthenticated]
