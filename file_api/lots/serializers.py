from rest_framework import serializers

from file_api.fichiers.serializers import QRCodeSerializer
from file_api.models import Etiquette, Site, InspectionType
from file_api.rapports.serializers import SiteSerializer, InspectionTypeSerializer


class EtiquetteAutoCreateSerializer(serializers.Serializer):
    site = serializers.PrimaryKeyRelatedField(queryset=Site.objects.all())
    inspectionType = serializers.PrimaryKeyRelatedField(queryset=InspectionType.objects.all())
    nombre = serializers.IntegerField(min_value=1)  # Le nombre d'étiquettes à créer


class EtiquetteSerializer(serializers.ModelSerializer):
    # Ajout des champs "site" et "inspectionType" pour les afficher comme des représentations de chaînes
    site = SiteSerializer(read_only=True)
    inspectionType = InspectionTypeSerializer(read_only=True)
    qrcode = QRCodeSerializer(read_only=True)
    class Meta:
        model = Etiquette
        fields = [
            'id',
            'inspectionType',
            'site',
            'numero',
            'qrcode',
            'image',
            'isAssigned',
        ]

    # Custom validation for unique together (inspectionType, site, numero)
    def validate(self, data):
        numero = data.get('numero')
        site = data.get('site')
        inspectionType = data.get('inspectionType')

        if Etiquette.objects.filter(numero=numero, site=site, inspectionType=inspectionType).exists():
            raise serializers.ValidationError("Cette étiquette existe déjà pour ce site et ce type d'inspection.")

        return data
