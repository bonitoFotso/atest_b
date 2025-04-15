from apps.certifications.models import CertificaType, Session, Certificat
from apps.documents.serializers import QRCodeSerializer, DossierSerializer
from rest_framework import serializers
from .models import  Participant



class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'



class CertificaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificaType
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    certificaType = CertificaTypeSerializer(read_only=True)

    class Meta:
        model = Session
        fields = '__all__'


class CertificatSerializer(serializers.ModelSerializer):
    participant = ParticipantSerializer(read_only=True)
    session = SessionSerializer(read_only=True)
    qrcode = QRCodeSerializer(read_only=True)
    dossier = DossierSerializer(read_only=True)

    class Meta:
        model = Certificat
        fields = '__all__'
