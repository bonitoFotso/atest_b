# serializers.py

from rest_framework import serializers
from .models import Participant, Formation

class FormationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Participant.objects.all(),
        required=False
    )

    class Meta:
        model = Formation
        fields = '__all__'

class ParticipantSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False)


    class Meta:
        model = Participant
        fields = '__all__'
