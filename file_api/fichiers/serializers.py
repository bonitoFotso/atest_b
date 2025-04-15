import uuid
from io import BytesIO

import segno
from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import serializers

from file_api.models import QRCode, Fichier, Dossier, Etiquette, LotEtiquette, Site
from file_api.rapports.serializers import InspectionTypeSerializer, ClientSerializerSite


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ['id', 'code', 'image', 'url', 'numero']
        read_only_fields = ['id', 'code', 'url', 'image']

    def create(self, validated_data):
        # Générer un UUID et une URL pour le QR code
        qr_uuid = uuid.uuid4()
        qr_url = f"{settings.BASE_URL}/rapport/{qr_uuid}/"

        # Générer le numéro du QR code
        numero = validated_data.get('numero', f"QR{QRCode.objects.count() + 1}")

        # Générer l'image QR code avec segno
        qr = segno.make(qr_url)
        qr_bytes = BytesIO()
        qr.save(qr_bytes, kind='png', border=0)
        qr_bytes.seek(0)  # Réinitialiser le pointeur du buffer

        # Chemin dynamique pour stocker les QR codes
        qr_filename = f"qr_code_{numero}.png"

        # Créer l'instance QRCode sans enregistrer encore
        qrcode_instance = QRCode(
            code=qr_uuid,
            url=qr_url,
            numero=numero
        )

        # Sauvegarder l'image dans le champ ImageField
        qrcode_instance.image.save(qr_filename, ContentFile(qr_bytes.read()), save=True)

        return qrcode_instance


class FichierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fichier  # Assuming you have a File model
        fields = '__all__'


class DossierSerializer(serializers.ModelSerializer):
    enfants = serializers.SerializerMethodField()
    fichiers = FichierSerializer(many=True, read_only=True)  # Sérialiser les fichiers liés au Dossier

    class Meta:
        model = Dossier
        fields = '__all__'

    def get_enfants(self, obj):
        # Sérialiser les dossiers enfants (self-référentiels)
        serializer = DossierSerializer(obj.enfants.all(), many=True)
        return serializer.data


class SiteListSerializer(serializers.ModelSerializer):
    client = ClientSerializerSite(read_only=True)
    class Meta:
        model = Site
        fields = '__all__'


class LotEtiquetteListSerializer(serializers.ModelSerializer):
    site = SiteListSerializer(read_only=True)
    inspectionType = InspectionTypeSerializer(read_only=True)

    class Meta:
        model = LotEtiquette
        fields = ['id', 'total', 'inspectionType', 'site']


class EtiquetteSerializer(serializers.ModelSerializer):
    qrcode = QRCodeSerializer(read_only=True)
    site = SiteListSerializer(read_only=True)
    inspectionType = InspectionTypeSerializer(read_only=True)

    class Meta:
        model = Etiquette
        fields = ['id', 'site', 'inspectionType', 'numero', 'qrcode', 'isAssigned']


class QRCodeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = '__all__'



class EtiquetteListSerializer(serializers.ModelSerializer):
    site = SiteListSerializer(read_only=True)
    inspectionType = InspectionTypeSerializer(read_only=True)
    qrcode = QRCodeListSerializer(read_only=True)

    class Meta:
        model = Etiquette
        fields = ['id', 'site', 'inspectionType', 'numero', 'qrcode', 'isAssigned']
