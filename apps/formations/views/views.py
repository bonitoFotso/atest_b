# views.py

from rest_framework import viewsets
from ..models import Participant, Formation
from ..serializers import ParticipantSerializer, FormationSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class ParticipantViewSet(viewsets.ModelViewSet):

    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]


class FormationViewSet(viewsets.ModelViewSet):

    queryset = Formation.objects.all()
    serializer_class = FormationSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
