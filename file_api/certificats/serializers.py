from rest_framework import serializers

from file_api.models import Session, Participant, Certificat, CertificaType


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'

class CertificatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificat
        fields = '__all__'

class CertificatSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Certificat
        fields = ['id','name', 'session', 'participant' ]


class CertificaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificaType
        fields = '__all__'


class SessionListSerializer(serializers.ModelSerializer):
    certificaType = CertificaTypeSerializer(read_only=True)
    class Meta:
        model = Session
        fields = '__all__'

class CertificatListSerializer(serializers.ModelSerializer):
    session = SessionListSerializer(read_only=True)
    participant = ParticipantSerializer(read_only=True)
    class Meta:
        model = Certificat
        fields = '__all__'