from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.inspections.models import Etiquette
from apps.inspections.serializers import EtiquetteSerializer


class EtiquetteLotView(generics.ListAPIView):
    serializer_class = EtiquetteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Récupérer toutes les étiquettes en les triant par client, site, inspectionType, et numéro (ordre croissant)
        return Etiquette.objects.all().order_by('client', 'site', 'inspectionType', 'numero')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        lots = []
        current_lot = []
        previous_etiquette = None

        # Parcourir toutes les étiquettes pour les regrouper en lots
        for etiquette in queryset:
            if previous_etiquette:
                # Vérifier si l'étiquette appartient au même lot que la précédente
                is_same_lot = (
                    etiquette.client == previous_etiquette.client and
                    etiquette.site == previous_etiquette.site and
                    etiquette.inspectionType == previous_etiquette.inspectionType and
                    etiquette.numero == previous_etiquette.numero + 1
                )

                if is_same_lot:
                    current_lot.append(etiquette)
                else:
                    if current_lot:  # Ajouter le lot précédent s'il existe
                        lots.append(current_lot)
                    current_lot = [etiquette]  # Commencer un nouveau lot
            else:
                current_lot.append(etiquette)

            previous_etiquette = etiquette

        # Ajouter le dernier lot si non vide
        if current_lot:
            lots.append(current_lot)

        # Trier les lots par l'identifiant (id) de la première étiquette de chaque lot, dans l'ordre décroissant
        lots.sort(key=lambda lot: lot[0].id, reverse=True)

        # Format de réponse : Sérialiser chaque lot et y associer un numéro de lot
        serialized_data = [
            {
                'lot_number': idx + 1,  # Numéro de lot commençant à
                'client': {
                    'id': lot[0].client.id,
                    'name': lot[0].client.name,  # Assurez-vous que le champ 'name' existe dans votre modèle Client
                },
                'site': {
                    'id': lot[0].site.id,
                    'name': lot[0].site.name,  # Assurez-vous que le champ 'name' existe dans votre modèle Site
                },
                'inspectionType': {
                    'id': lot[0].inspectionType.id,
                    'name': lot[0].inspectionType.name,
                    # Assurez-vous que le champ 'name' existe dans votre modèle InspectionType
                },
                'etiquettes': self.get_serializer(lot, many=True).data
            }
            for idx, lot in enumerate(lots)
        ]

        return Response(serialized_data)
