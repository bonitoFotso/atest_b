from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.staticfiles.storage import staticfiles_storage
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import zipfile
import io
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
import uuid
import segno
from io import BytesIO

from apps.certifications.utils import format_certificate_text

month_translation = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
}

def convert_date_to_month_year(date_str):
    """
    Convertit une date au format '22 Novembre 2024' en '11/24'.

    Args:
        date_str (str): La date sous forme de chaîne, ex. "22 Novembre 2024".

    Returns:
        str: La date au format "MM/YY", ex. "11/24".
    """
    try:
        # Convertir la date en objet datetime
        date_obj = datetime.strptime(date_str, '%d %B %Y')
        # Extraire le mois et l'année pour créer le format MM/YY
        return date_obj.strftime('%m/%y')
    except ValueError:
        raise ValueError("Format de date incorrect. Utilisez le format '22 Novembre 2024'.")


class GenerateCertificateView(APIView):
    def post(self, request, *args, **kwargs):
        # Récupérer les données depuis le formulaire
        client = request.data.get("client")
        date_delivrance = request.data.get("date_delivrance")
        date_formation = request.data.get("date_formation")


        # Convertir la date de formation en un format dynamique
        def format_date_range(date_debut, date_fin):
            try:
                # Parse les dates
                start_date = datetime.strptime(date_debut, "%d/%m/%Y")
                end_date = datetime.strptime(date_fin, "%d/%m/%Y")

                # Obtenir les composants des dates
                day_start = start_date.day
                day_end = end_date.day
                month_name = month_translation[start_date.month]
                year = start_date.year

                # Calculer la durée
                duration_days = (end_date - start_date).days + 1

                # Formater la sortie
                formatted_date = f"{day_start} {month_name} {year}" if date_debut == date_fin else f"{day_start} au {day_end} {month_name} {year}"

                return {
                    'formatted_date': formatted_date,
                    'duration': duration_days,
                    'start_date': start_date,
                    'end_date': end_date
                }
            except ValueError:
                return {
                    'formatted_date': f"{date_debut} au {date_fin}",
                    'duration': None,
                    'start_date': None,
                    'end_date': None
                }

        # Exemple d'utilisation

        def format_date(date_str):
            try:
                # Support both 2-digit and 4-digit year formats
                if len(date_str.split('/')[2]) == 4:
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                else:
                    date_obj = datetime.strptime(date_str, "%d/%m/%y")

                day = date_obj.day
                month = month_translation[date_obj.month]
                year = date_obj.year

                return f"{day} {month} {year}"
            except ValueError:
                return date_str



        # Charger le fichier Excel
        excel_file = request.FILES.get("excel_file")
        if not excel_file:
            return Response({"error": "Fichier Excel requis."}, status=status.HTTP_400_BAD_REQUEST)

        df = pd.read_excel(excel_file)

        if 'Nom' not in df.columns:
            return Response({"error": "Le fichier Excel doit contenir une colonne 'Nom(s)'."},
                            status=status.HTTP_400_BAD_REQUEST)

        image_path = staticfiles_storage.path('images/att1.png')
        font_path_alex = staticfiles_storage.path('fonts/this.ttf')
        font_path_helvetica = staticfiles_storage.path('fonts/Helvetica.ttf')
        font_path_helvetica_bold = staticfiles_storage.path('fonts/Helvetica-Bold.ttf')


        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            habilitation_counter = 1

            for idx, row in df.iterrows():
                client = row.get('Client')
                date_delivrance = row.get('date de délivrance', date_delivrance)
                date_delivrance = format_date(date_delivrance)
                objet_formation = row.get('Titre')
                date_f = row.get('Date de la formation', client)
                debut_formation = row.get('Date début')
                fin_formations = row.get("Date fin")
                dates = format_date_range(debut_formation, fin_formations)
                temps_presence = f"{dates['duration'] * 8} heures" if dates['duration'] else "8 heures"
                print(f"Date de la formation : {dates['formatted_date']}")

                # converted_date = convert_date_to_month_year(date_f)

                numero_attestation = row.get('numéro attestation')
                nom_participant = row['Nom']
                prenom = row.get('Prénom', '')
                client = row.get('Client')
                habilitation_counter += 1

                if pd.notna(prenom):
                    nom_participant = f"{nom_participant} {prenom}"

                # Générer un UUID pour chaque participant
                participant_uuid = uuid.uuid4()
                url = f"https://kesdocs.vercel.app/verify/{participant_uuid}"

                # Créer le QR code avec segno
                qr = segno.make(url)
                qr_image = BytesIO()
                qr.save(qr_image, kind='png', border=0, scale=3)  # Sauvegarder le QR code en mémoire
                qr_image.seek(0)  # Rewind pour pouvoir l'utiliser

                # Ouvrir l'image de fond
                with Image.open(image_path) as img:
                    draw = ImageDraw.Draw(img)
                    width, height = img.size

                    # Charger les polices
                    font_helvetica = ImageFont.truetype(font_path_helvetica, size=40)
                    font_helvetica_bold = ImageFont.truetype(font_path_helvetica_bold, size=40)
                    font_helvetica_small = ImageFont.truetype(font_path_helvetica, size=20)
                    font_helvetica_bold_small = ImageFont.truetype(font_path_helvetica_bold, size=22)

                    center_x = width / 2

                    # Nom du participant centré
                    participant_text = f"{nom_participant}"
                    max_width = 1700

                    # Ajuster la taille de la police pour le nom du participant
                    font_size = 100
                    font_alex = ImageFont.truetype(font_path_alex, size=font_size)
                    # Utiliser font.getbbox au lieu de font.getsize
                    bbox = font_alex.getbbox(participant_text)
                    participant_width = bbox[2] - bbox[0]
                    participant_height = bbox[3] - bbox[1]
                    while participant_width > max_width and font_size > 10:
                        font_size -= 1
                        font_alex = ImageFont.truetype(font_path_alex, size=font_size)
                        bbox = font_alex.getbbox(participant_text)
                        participant_width = bbox[2] - bbox[0]
                        participant_height = bbox[3] - bbox[1]

                    draw.text((center_x - participant_width / 2,   680 - participant_height / 2),
                              participant_text,
                              font=font_alex,
                              fill=(31, 89, 156))

                    text = f"a suivi la **{objet_formation}** avec succès"
                    final_y = format_certificate_text(
                        draw,
                        text,
                        center_x=1000,  # Center point
                        start_y=820,  # Starting Y position
                        max_width=1850,
                        line_height=50
                    )

                    # Texte pour le client (nom en gras uniquement)
                    client_text = f"de la société **{client}**, "
                    client_1, client_2, client_3 = client_text.split("**")

                    bbox = font_helvetica.getbbox(client_1)
                    client_1_width = bbox[2] - bbox[0]
                    bbox = font_helvetica_bold.getbbox(client_2)
                    client_2_width = bbox[2] - bbox[0]
                    bbox = font_helvetica.getbbox(client_3)
                    client_3_width = bbox[2] - bbox[0]

                    client_word_width = client_1_width + client_2_width + client_3_width

                    current_x = center_x - client_word_width / 2
                    current_y =   750

                    draw.text((current_x, current_y), client_1, font=font_helvetica, fill=(0, 0, 0))
                    current_x += client_1_width
                    draw.text((current_x, current_y), client_2, font=font_helvetica_bold, fill=(0, 0, 0))
                    current_x += client_2_width
                    draw.text((current_x, current_y), client_3, font=font_helvetica, fill=(0, 0, 0))

                    # Dates et temps de présence
                    date_text = f"Date de la formation : *{dates['formatted_date']}"
                    date_1, date_2 = date_text.split("*")

                    temps_presence_text = f"Temps de présence : -{temps_presence}"
                    temps_1, temps_2 = temps_presence_text.split("-")

                    draw.text((195,   930), date_1, font=font_helvetica, fill=(0, 0, 0))
                    bbox = font_helvetica.getbbox(date_1)
                    date_1_width = bbox[2] - bbox[0]
                    draw.text((195 + date_1_width,   930), date_2, font=font_helvetica_bold, fill=(0, 0, 0))

                    draw.text((195,   980), temps_1, font=font_helvetica, fill=(0, 0, 0))
                    bbox = font_helvetica.getbbox(temps_1)
                    temps_1_width = bbox[2] - bbox[0]
                    draw.text((195 + temps_1_width,   980), temps_2, font=font_helvetica_bold, fill=(0, 0, 0))

                    # Numéro d'attestation
                    att_text = f"N D'ATTESTATION : *{numero_attestation}"
                    att_1, att_2 = att_text.split("*")
                    draw.text((1400,   1210), att_1, font=font_helvetica_small, fill=(0, 0, 0))
                    bbox = font_helvetica_small.getbbox(att_1)
                    att_1_width = bbox[2] - bbox[0]
                    draw.text((1400 + att_1_width,   1210), att_2, font=font_helvetica_bold_small, fill=(0, 0, 0))

                    # Date de délivrance
                    delivrance_text = f"DATE DE DELIVRANCE : *{date_delivrance}"
                    delivrance_1, delivrance_2 = delivrance_text.split("*")
                    draw.text((1400,   1288), delivrance_1, font=font_helvetica_small, fill=(0, 0, 0))
                    bbox = font_helvetica_small.getbbox(delivrance_1)
                    delivrance_1_width = bbox[2] - bbox[0]
                    draw.text((1400 + delivrance_1_width,   1288), delivrance_2, font=font_helvetica_bold_small, fill=(0, 0, 0))

                    # Ajouter le QR code
                    qr_width = 200
                    qr_height = 200
                    qr_img = Image.open(qr_image)
                    qr_img = qr_img.resize((qr_width, qr_height))
                    img.paste(qr_img, (1570,   915))

                    # Sauvegarder l'image en mémoire
                    image_buffer = io.BytesIO()
                    img.save(image_buffer, format='PNG')
                    image_buffer.seek(0)

                # Ajouter l'image au ZIP
                image_name = f"image/attestation_{nom_participant}.png"
                zip_file.writestr(image_name, image_buffer.getvalue())

                # Générer le PDF en utilisant ReportLab et en intégrant l'image


                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=(width, height))

                # Charger l'image du certificat
                certificate_image = ImageReader(image_buffer)
                c.drawImage(certificate_image, 0, 0, width=width, height=height)

                c.showPage()
                c.save()

                # Ajouter le PDF au ZIP
                pdf_name = f"pdf/attestation_{nom_participant}.pdf"
                zip_file.writestr(pdf_name, pdf_buffer.getvalue())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename="attestations.zip"'
        return response
