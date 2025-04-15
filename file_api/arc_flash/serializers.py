from rest_framework import serializers

from file_api.fichiers.serializers import QRCodeSerializer, DossierSerializer, SiteListSerializer
from file_api.models import ArcFlashLabel

class ArcFlashLabelSerializer(serializers.ModelSerializer):
    qrcode = QRCodeSerializer(read_only=True)
    dossier = DossierSerializer(read_only=True)
    site = SiteListSerializer(read_only=True)
    class Meta:
        model = ArcFlashLabel
        fields = '__all__'
