import io
import os
import tempfile
import zipfile
from PIL import ImageDraw, Image
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .generate_certificate import generate_habilitation_certificate
from .data import load_data_from_excel
import json
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


# Serializer pour valider le fichier Excel
class HabilitationFileSerializer(serializers.Serializer):
    file = serializers.FileField()


class HabilitationGenerateView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        print("HabilitationGenerateView")
        # Valider le fichier reçu
        serializer = HabilitationFileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Charger le fichier Excel et vérifier son contenu
        excel_file = serializer.validated_data['file']
        try:
            all_data = load_data_from_excel(excel_file)
            print(all_data)
        except Exception as e:
            return Response({"error": f"Erreur lors du traitement du fichier Excel : {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Charger les coordonnées depuis le fichier JSON
        coordonnees_path = os.path.join(settings.BASE_DIR, 'static', 'json', 'coordonnees_HE.json')
        try:
            with open(coordonnees_path, 'r') as json_file:
                coordonnees_rectangles = json.load(json_file)
        except FileNotFoundError:
            return Response({"error": "Le fichier coordonnees_HE.json est introuvable."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Dossier temporaire pour stocker les fichiers
        temp_dir = tempfile.mkdtemp()
        zip_buffer = io.BytesIO()

        try:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, data in enumerate(all_data):
                    nom_personne = data.get("Nom", {}).get("valeur", f"personne_{i + 1}")
                    prenom = data.get("Prénom", {}).get("valeur", "")
                    nom_personne_sanitized = f"{nom_personne}_{prenom}".replace(" ", "_").replace("__", "_")

                    # Générer les images recto et verso
                    recto_path = os.path.join(temp_dir, f"habilitation_{nom_personne_sanitized}_recto.jpeg")
                    verso_path = os.path.join(temp_dir, f"habilitation_{nom_personne_sanitized}_verso.jpeg")
                    verso_template = os.path.join(settings.STATIC_ROOT, 'images', 'he_verso.png')
                    generate_habilitation_certificate(data, coordonnees_rectangles, recto_path)

                    # Charger et enregistrer l'image verso directement
                    if os.path.exists(verso_template):
                        Image.open(verso_template).save(verso_path)

                    # Créer un PDF avec recto et verso
                    pdf_buffer = io.BytesIO()
                    img_recto = Image.open(recto_path)
                    img_verso = Image.open(verso_path)
                    width, height = img_recto.size

                    c = canvas.Canvas(pdf_buffer, pagesize=(width, height))
                    c.drawImage(ImageReader(img_recto), 0, 0, width=width, height=height)
                    c.showPage()
                    c.drawImage(ImageReader(img_verso), 0, 0, width=width, height=height)
                    c.showPage()
                    c.save()
                    img_recto.close()
                    img_verso.close()

                    # Ajouter les fichiers au ZIP
                    zipf.write(recto_path, os.path.basename(recto_path))
                    zipf.write(verso_path, os.path.basename(verso_path))
                    pdf_name = f"pdf/attestation_{nom_personne_sanitized}.pdf"
                    zipf.writestr(pdf_name, pdf_buffer.getvalue())

            # Retourner le fichier ZIP en réponse
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type="application/zip")
            response['Content-Disposition'] = 'attachment; filename=habilitations.zip'
            return response

        except Exception as e:
            return Response({"error": f"Erreur lors de la génération des certificats : {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            # Nettoyer les fichiers temporaires
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
