from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.staticfiles.storage import staticfiles_storage
from PIL import Image
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import Color
import zipfile
import io
import tempfile


class GenerateCertificateView(APIView):
    def post(self, request, *args, **kwargs):
        # Récupérer les données depuis le formulaire
        objet_formation = request.data.get("objet_formation", "PREVENTION DES RISQUES LIES AU TRAVAIL EN HAUTEUR")
        client = request.data.get("client", "BOISSONS DU CAMEROUN")
        date_delivrance = request.data.get("date_delivrance", "11/11/24")
        date_formation = request.data.get("date_formation", "du 8 au 9 /11/24")
        temps_presence = request.data.get("temps_presence", "16 heures")

        # Charger le fichier Excel
        excel_file = request.FILES.get("excel_file")
        if not excel_file:
            return Response({"error": "Fichier Excel requis."}, status=status.HTTP_400_BAD_REQUEST)

        df = pd.read_excel(excel_file)

        # Vérifier les colonnes du fichier Excel
        if 'nom_participant' not in df.columns:
            return Response({"error": "Le fichier Excel doit contenir une colonne 'nom_participant'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Charger l'image de base depuis le dossier static
        image_path = staticfiles_storage.path('images/att1.png')

        # Enregistrer la police Alex Brush dans reportlab
        font_path = staticfiles_storage.path('fonts/AlexBrush-Regular.ttf')
        pdfmetrics.registerFont(TTFont('AlexBrush', font_path))

        # Numéro d’attestation initial
        numero_base = "KES/F/TH/YDE_SABC/11/24 - "

        # Créer un fichier ZIP en mémoire
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, row in df.iterrows():
                numero_attestation = f"{numero_base}{idx + 1}"
                nom_participant = row['nom_participant']

                # Ouvrir l'image pour obtenir ses dimensions
                with Image.open(image_path) as img:
                    width, height = img.size  # Dimensions d'origine de l'image en paysage

                    # Créer un PDF avec les mêmes dimensions que l'image
                    pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(pdf_buffer, pagesize=(width, height))

                    # Utiliser un fichier temporaire pour l'image
                    with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as temp_image_file:
                        img.save(temp_image_file, format="PNG")
                        temp_image_file.flush()

                        # Placer l'image sans redimensionnement
                        c.drawImage(temp_image_file.name, 0, 0, width=width, height=height)

                # Ajouter le texte avec gestion du retour à la ligne et du gras
                center_x = width / 2  # Point central horizontal de la page

                # Texte principal avec retour à la ligne et mise en gras de `objet_formation`
                title_text = f"a suivi la formation en {objet_formation} avec succès"
                title_words = title_text.split()  # Diviser en mots pour gérer le retour à la ligne
                line_height = 40  # Hauteur entre chaque ligne
                current_y = height - 860

                # Variables pour construire chaque ligne
                line = ""
                max_width = 600  # Largeur maximale avant retour à la ligne

                c.setFont("Helvetica", 40)
                for word in title_words:
                    test_line = f"{line} {word}".strip()
                    line_width = pdfmetrics.stringWidth(test_line, "Helvetica", 40)

                    if line_width > max_width:
                        # Écrire la ligne existante si elle dépasse la largeur maximale
                        if "formation en" in line:
                            # Écrire "formation en" en texte normal et `objet_formation` en gras
                            normal_part, bold_part = line.split("formation en", 1)
                            c.drawString(center_x - pdfmetrics.stringWidth(normal_part, "Helvetica", 40) / 2, current_y,
                                         normal_part + "formation en")
                            c.setFont("Helvetica-Bold", 40)
                            c.drawString(center_x - pdfmetrics.stringWidth(bold_part, "Helvetica-Bold", 40) / 2,
                                         current_y, bold_part)
                            c.setFont("Helvetica", 40)
                        else:
                            c.drawString(center_x - line_width / 2, current_y, line)
                        line = word  # Nouvelle ligne
                        current_y -= line_height  # Descendre pour la prochaine ligne
                    else:
                        line = test_line  # Ajouter le mot à la ligne en cours

                # Écrire la dernière ligne si elle existe
                if line:
                    c.drawString(center_x - pdfmetrics.stringWidth(line, "Helvetica", 40) / 2, current_y, line)

                # Ajouter d'autres sections comme le client
                c.setFont("Helvetica", 40)
                c.setFillColor(Color(0.0, 0.5, 0.2))
                client_text = f"de la societe {client},"
                client_width = pdfmetrics.stringWidth(client_text, "Helvetica", 30)
                c.drawString(center_x - client_width / 2, height - 800, client_text)

                # Nom du participant centré
                c.setFont("AlexBrush", 120)
                c.setFillColor(Color(0.5, 0.0, 0.0))
                participant_text = f"{nom_participant}"
                participant_width = pdfmetrics.stringWidth(participant_text, "AlexBrush", 120)
                c.drawString(center_x - participant_width / 2, height - 740, participant_text)

                # Numéro d'attestation et autres détails
                c.setFont("Helvetica", 25)
                c.setFillColor(Color(0, 0, 0))
                c.drawString(1400, height - 1230, f"N D'ATTESTATION : {numero_attestation}")
                c.drawString(1400, height - 1300, f"Délivré le : {date_delivrance}")

                # Dates et temps de présence
                c.setFont("Helvetica", 40)
                c.drawString(195, height - 930, f"Date de la formation : {date_formation}")
                c.drawString(195, height - 980, f"Temps de présence : {temps_presence} heures")

                # Finaliser la page et sauvegarder le PDF
                c.showPage()
                c.save()

                # Ajouter le PDF au fichier ZIP
                pdf_name = f"attestation_{nom_participant}.pdf"
                zip_file.writestr(pdf_name, pdf_buffer.getvalue())

        # Préparer le fichier ZIP pour la réponse
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename="attestations.zip"'

        return response
