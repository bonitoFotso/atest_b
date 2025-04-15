# apps/inspections/serializers.py

from rest_framework import serializers

from apps.clients.models import Client
from apps.geography.models import Site
from apps.inspections.models import (
    InspectionType, LotEtiquette, Etiquette, Rapport, ArcFlashLabel
)
from apps.geography.serializers import SiteDetailSerializer
from apps.documents.serializers import QRCodeSerializer
from apps.clients.serializers import AffaireDetailSerializer, ClientDetailSerializer


class InspectionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionType
        fields = '__all__'

class LotEtiquetteSerializer(serializers.ModelSerializer):
    inspectionType = InspectionTypeSerializer(read_only=True)
    site = SiteDetailSerializer(read_only=True)

    class Meta:
        model = LotEtiquette
        fields = '__all__'

class EtiquetteSerializer(serializers.ModelSerializer):
    inspectionType = InspectionTypeSerializer(read_only=True)
    site = SiteDetailSerializer(read_only=True)
    qrcode = QRCodeSerializer(read_only=True)
    client = ClientDetailSerializer(read_only=True)
    class Meta:
        model = Etiquette
        fields = '__all__'

class EtiquetteAutoCreateSerializer(serializers.Serializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    site = serializers.PrimaryKeyRelatedField(queryset=Site.objects.all())
    inspectionType = serializers.PrimaryKeyRelatedField(queryset=InspectionType.objects.all())
    nombre = serializers.IntegerField(min_value=1)  # Le nombre d'étiquettes à créer

class RapportSerializer(serializers.ModelSerializer):
    site = SiteDetailSerializer(read_only=True)
    inspectionType = InspectionTypeSerializer(read_only=True)
    etiquette = EtiquetteSerializer(read_only=True)
    qrcode = QRCodeSerializer(read_only=True)
    business = AffaireDetailSerializer(read_only=True)

    class Meta:
        model = Rapport
        fields = '__all__'

class ArcFlashLabelSerializer(serializers.ModelSerializer):
    site = SiteDetailSerializer(read_only=True)
    qrcode = QRCodeSerializer(read_only=True)

    class Meta:
        model = ArcFlashLabel
        fields = '__all__'
