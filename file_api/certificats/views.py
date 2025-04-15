from rest_framework import generics

from file_api.certificats.serializers import SessionSerializer, ParticipantSerializer, CertificatSerializer, \
    CertificatSerializerCreate, CertificatListSerializer
from file_api.models import Session, Participant, Certificat, QRCode, Dossier, Fichier
from rest_framework.parsers import MultiPartParser, FormParser

import uuid
from rest_framework import generics, status
from rest_framework.response import Response
from django.conf import settings
from .serializers import CertificatSerializer
from io import BytesIO
import segno
from django.core.files.base import ContentFile


class CertificatList(generics.ListAPIView):
    queryset = Certificat.objects.all()
    serializer_class = CertificatListSerializer

class CertificatListCreateView(generics.ListCreateAPIView):
    queryset = Certificat.objects.all()
    serializer_class = CertificatSerializerCreate

    def perform_create(self, serializer):
        """
        Custom create method to generate the QR code after creating the Certificat.
        """
        # Save the Certificat instance first
        certificat = serializer.save()

        # Generate QR Code dynamically
        qr_uuid = uuid.uuid4()
        qr_url = f"{settings.BASE_URL}/certificat/{qr_uuid}/"
        qr_code_image = self.generate_qr_code_image(qr_url, qr_uuid)

        # Create the QRCode instance
        qr_code = QRCode.objects.create(
            code=qr_uuid,
            url=qr_url,
            image=qr_code_image,
            numero=f"Cert-{certificat.id}"
        )

        # Create or get hierarchical Dossier structure
        dossier_annee, _ = Dossier.objects.get_or_create(name=str(certificat.session.annee), parent=None)
        dossier_certificats, _ = Dossier.objects.get_or_create(name='certificats', parent=dossier_annee)
        dossier_certificats_type, _ = Dossier.objects.get_or_create(name=certificat.session.certificaType.name, parent=dossier_certificats)
        dossier_session, _ = Dossier.objects.get_or_create(name=f"{certificat.session.mois}/{certificat.session.annee}", parent=dossier_certificats_type)
        dossier_participant, _ = Dossier.objects.get_or_create(name=f"{certificat.participant.nom} {certificat.participant.prenom}", parent=dossier_session)

        # Assign the Dossier and QR code to the Certificat
        certificat.dossier = dossier_participant
        certificat.qrcode = qr_code
        certificat.save()

        # Create a Fichier record for the QR code
        Fichier.objects.get_or_create(
            name=qr_code.numero,
            dossier=dossier_participant,
            fichier=qr_code.image,
            type='QRCode'
        )

        return certificat

    def generate_qr_code_image(self, qr_url, qr_uuid):
        """
        Generate the QR code and return the file.
        """
        qr = segno.make(qr_url)
        qr_bytes = BytesIO()
        qr.save(qr_bytes, kind='png')

        qr_filename = f"qr_code_{qr_uuid}.png"
        qr_code_image = ContentFile(qr_bytes.getvalue(), qr_filename)

        return qr_code_image

    def create(self, request, *args, **kwargs):
        """
        Override create method to return the Certificat and its QR code URL.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificat = self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response({
            "certificat": serializer.data,
            "qr_code_url": certificat.qrcode.image.url  # Return the QR code URL
        }, status=status.HTTP_201_CREATED, headers=headers)


class CertificatFileUploadView(generics.UpdateAPIView):
    queryset = Certificat.objects.all()
    serializer_class = CertificatSerializer
    parser_classes = (MultiPartParser, FormParser)

    def update(self, request, *args, **kwargs):
        """
        Update the existing Certificat by adding a file to it.
        """
        certificat = self.get_object()
        fichier = request.FILES.get('fichier', None)

        if not fichier:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Attach the file to the certificat
        fichier_certificat, _ = Fichier.objects.get_or_create(name = certificat.name, dossier = certificat.dossier, fichier = fichier, type = 'Certificat')
        certificat.fichier = fichier
        certificat.save()

        return Response({
            "message": "File uploaded successfully.",
            "certificat": CertificatSerializer(certificat).data
        }, status=status.HTTP_200_OK)

class SessionListCreateView(generics.ListCreateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

class SessionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

class ParticipantListCreateView(generics.ListCreateAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

class ParticipantRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer


class CertificatRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Certificat.objects.all()
    serializer_class = CertificatSerializer