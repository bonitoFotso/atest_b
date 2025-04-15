# apps/certifications/views.py
from rest_framework.permissions import IsAuthenticated

from apps.certifications.models import CertificaType, Session

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
import os
from rest_framework import viewsets
from apps.habilitations.models import Employeur, Responsable, Participant, Habilitation, Inscription
from apps.habilitations.serializers import (
    EmployeurSerializer,
    ResponsableSerializer,
    ParticipantSerializer,
    HabilitationSerializer,
    InscriptionSerializer
)
class ImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        # Vérifiez si le fichier est inclus dans la requête
        if 'photo' not in request.FILES:
            return Response({"error": "Aucun fichier envoyé."}, status=status.HTTP_400_BAD_REQUEST)

        # Récupérez le fichier envoyé
        image = request.FILES['photo']

        # Enregistrez l'image dans le dossier média
        file_path = default_storage.save(f"images/{image.name}", image)
        file_url = os.path.join(settings.MEDIA_URL, file_path)

        # Retournez l'URL de l'image en réponse
        return Response({"url": request.build_absolute_uri(file_url)}, status=status.HTTP_201_CREATED)



class EmployeurViewSet(viewsets.ModelViewSet):
    queryset = Employeur.objects.all()
    serializer_class = EmployeurSerializer

class ResponsableViewSet(viewsets.ModelViewSet):
    queryset = Responsable.objects.all()
    serializer_class = ResponsableSerializer

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

class HabilitationViewSet(viewsets.ModelViewSet):
    queryset = Habilitation.objects.all()
    serializer_class = HabilitationSerializer

class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
