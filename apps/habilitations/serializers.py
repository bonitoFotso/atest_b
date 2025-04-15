from apps.certifications.models import CertificaType, Session, Certificat
from apps.documents.serializers import QRCodeSerializer, DossierSerializer
from rest_framework import serializers
from .models import Employeur, Responsable, Participant, Habilitation, Inscription

class EmployeurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employeur
        fields = '__all__'

class ResponsableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsable
        fields = '__all__'

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'

class HabilitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habilitation
        fields = '__all__'

class InscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscription
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
