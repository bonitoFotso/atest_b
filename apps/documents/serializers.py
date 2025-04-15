# apps/documents/serializers.py

from rest_framework import serializers
from apps.documents.models import QRCode, Dossier, Fichier

class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = '__all__'

class DossierSerializer(serializers.ModelSerializer):
    enfants = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Dossier.objects.all(), required=False
    )

    class Meta:
        model = Dossier
        fields = '__all__'

class FichierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fichier
        fields = '__all__'
