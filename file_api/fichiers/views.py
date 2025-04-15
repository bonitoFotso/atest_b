import uuid
from io import BytesIO

import segno
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.http import FileResponse

from django.conf import settings
from file_api.fichiers.serializers import QRCodeSerializer, \
    EtiquetteSerializer, EtiquetteListSerializer, DossierSerializer, FichierSerializer
from file_api.models import QRCode, Etiquette, Site, InspectionType, Dossier, Fichier

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

def download_qr_image(request, qr_code_id):
    """
    Vue pour télécharger l'image du QR code
    :param request: La requête HTTP
    :param qr_code_id: L'ID ou le code UUID du QR code
    :return: Une réponse avec l'image du QR code
    """
    try:
        # Récupérer le QR code à partir de l'ID
        qr_code = get_object_or_404(QRCode, pk=qr_code_id)

        # Ouvrir l'image du QR code
        with open(qr_code.image.path, 'rb') as image_file:
            response = HttpResponse(image_file.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{qr_code.numero}_qrcode.png"'
            return response

    except QRCode.DoesNotExist:
        raise Http404("QR code non trouvé.")


# QRCode CRUD
class QRCodeListCreateAPIView(generics.ListCreateAPIView):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer
    def perform_create(self, serializer):
        qrcode = serializer.save()

class GenerateQRCodeView(generics.CreateAPIView):
    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            qrcode_instance = serializer.save()
            return Response(QRCodeSerializer(qrcode_instance).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DownloadQRCodeView(generics.RetrieveAPIView):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qrcode = self.get_object()
        print(qrcode.image)

        # Check if the QR code has an image
        if not qrcode.image:
            return Response({"error": "QR code image not found."}, status=status.HTTP_404_NOT_FOUND)

        # Return the image as a file response
        response = FileResponse(qrcode.image.open(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{qrcode.id}_qrcode.png"'
        return response


class QRCodeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer


# Folder CRUD
class DossierListCreateView(generics.ListCreateAPIView):
    queryset = Dossier.objects.all()
    serializer_class = DossierSerializer


class DossierRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dossier.objects.all()
    serializer_class = DossierSerializer


class FichierListCreateView(generics.ListCreateAPIView):
    queryset = Fichier.objects.all()
    serializer_class = FichierSerializer


class FichierRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fichier.objects.all()
    serializer_class = FichierSerializer


class EtiquetteListCreateAPIView(generics.ListCreateAPIView):
    queryset = Etiquette.objects.all()
    serializer_class = EtiquetteSerializer


class LotEtiquetteListView(generics.ListAPIView):
    serializer_class = EtiquetteListSerializer

    def get_queryset(self):
        lot_id = self.kwargs.get('lot_id')
        return Etiquette.objects.filter(lot=lot_id)


class EtiquetteRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Etiquette.objects.all()
    serializer_class = EtiquetteSerializer


class BulkCreateEtiquetteAPIView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        site_id = request.data.get('site')
        inspection_type_id = request.data.get('inspectionType')
        total = int(request.data.get('number', 0))

        if not site_id or not inspection_type_id or total <= 0:
            return Response({"error": "site_id, inspection_type_id, and a positive total number are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            site = Site.objects.get(id=site_id)
            inspection_type = InspectionType.objects.get(id=inspection_type_id)
        except Site.DoesNotExist:
            return Response({"error": "Site not found."}, status=status.HTTP_404_NOT_FOUND)
        except InspectionType.DoesNotExist:
            return Response({"error": "Inspection type not found."}, status=status.HTTP_404_NOT_FOUND)

        # Récupérer le dernier numéro d'étiquette créé pour ce site et ce type d'inspection
        last_etiquette = Etiquette.objects.filter(site=site, inspectionType=inspection_type).order_by('number').last()
        next_number = (int(last_etiquette.number) + 1) if last_etiquette else 1
        print(last_etiquette)
        print(next_number)

        created_etiquettes = []

        for i in range(total):
            if not Etiquette.objects.filter(site=site, inspectionType=inspection_type, number=next_number).exists():
                etiquette = Etiquette.objects.create(
                    number=next_number,
                    site=site,
                    inspectionType=inspection_type
                )
                created_etiquettes.append({
                    "id": etiquette.id,
                    "number": etiquette.number,
                    "site": etiquette.site.id,
                    "inspectionType": etiquette.inspectionType.id
                })
            next_number += 1

        if not created_etiquettes:
            return Response({"message": "No new etiquettes were created."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"created_etiquettes": created_etiquettes}, status=status.HTTP_201_CREATED)
