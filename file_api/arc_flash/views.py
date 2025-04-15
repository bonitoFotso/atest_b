from datetime import datetime
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.core.files.base import ContentFile
import pandas as pd
import zipfile
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import uuid
import segno

from apps.utils import get_font_for_text
from file_api.arc_flash.serializers import ArcFlashLabelSerializer
from file_api.models import Site, Dossier, Fichier, QRCode, ArcFlashLabel
from django.conf import settings
import os


class GenerateArcFlashLabelsView(APIView):
    def post(self, request, *args, **kwargs):
        site_id = request.data.get('site')
        excel_file = request.FILES.get('fichier')
        date_i = request.data.get('date_inspection')
        date_ins = datetime.strptime(date_i, "%Y-%m-%d")

        if not excel_file or not site_id:
            return Response({"error": "Aucun fichier ou site fourni"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            site_obj = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            return Response({"error": "Site non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        # Charger les données depuis le fichier Excel
        df = pd.read_excel(excel_file, sheet_name='Export')
        font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')

        # Charger l'image de base pour l'étiquette
        base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'arcflash.png')
        base_image = Image.open(base_image_path)

        # Liste pour stocker les étiquettes générées
        etiquettes = []
        zip_buffer = BytesIO()  # Buffer pour stocker le fichier ZIP
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for i, row in df.iterrows():
                try:
                    qrcode = generate_qr_code(uuid.uuid4(), site_obj, row['Unnamed: 0'])
                    output_image = self.generate_label(row, qrcode, font_path, site_obj)

                    zip_file.writestr(f"etiquette_{qrcode.numero}.png", output_image.read())
                    etiquettes.append({
                        'filename': f"etiquette_{qrcode.numero}.png",
                        'content': output_image.read()
                    })

                    # Créer ou obtenir les dossiers requis dans la base de données
                    dossier_annee, _ = Dossier.objects.get_or_create(name=str(date_ins.year), parent=None)
                    dossier_rapports, _ = Dossier.objects.get_or_create(name='rapports', parent=dossier_annee)
                    dossier_client, _ = Dossier.objects.get_or_create(name=site_obj.client.name,
                                                                      parent=dossier_rapports)
                    dossier_site, _ = Dossier.objects.get_or_create(name=site_obj.name, parent=dossier_client)
                    dossier_type_inspection, _ = Dossier.objects.get_or_create(name="ArcFlash", parent=dossier_site)
                    dossier_numero_rapport, _ = Dossier.objects.get_or_create(name=qrcode.numero,
                                                                              parent=dossier_type_inspection)

                    # Sauvegarder les fichiers dans la base de données
                    fichier_etiquette, _ = Fichier.objects.get_or_create(
                        name=qrcode.numero, dossier=dossier_numero_rapport,
                        fichier=output_image, type='Etiquette'
                    )
                    fichier_qr, _ = Fichier.objects.get_or_create(
                        name=qrcode.numero, dossier=dossier_numero_rapport,
                        fichier=qrcode.image, type='QRCode'
                    )

                    # Créer l'objet ArcFlashLabel
                    acr = self.create_arcflash_label_object(
                        row, site_obj, qrcode, date_ins, output_image, dossier_numero_rapport
                    )

                except Exception as e:
                    print(f"Erreur lors du traitement de la ligne {i}: {e}")

        # Préparer le fichier ZIP pour stockage
        zip_buffer.seek(0)
        zip_filename = f"arc_flash/{site_obj.client.name}/{site_obj.name}/etiquettes_arcflash.zip"

        # Créer le chemin complet si nécessaire
        zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
        os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)  # Créer les répertoires manquants

        # Sauvegarder le fichier ZIP sur le disque
        with open(zip_file_path, 'wb') as f:
            f.write(zip_buffer.getvalue())

        # Sauvegarder le fichier ZIP dans la base de données (modèle Fichier)
        fichier_zip, _ = Fichier.objects.get_or_create(
            name="etiquettes_arcflash.zip",
            dossier=dossier_type_inspection,
            fichier=ContentFile(zip_buffer.getvalue(), zip_filename),
            type="ZIP"
        )

        # Préparer la réponse HTTP pour télécharger le fichier
        zip_buffer.seek(0)
        response = HttpResponse(fichier_zip.fichier, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="etiquettes_arcflash.zip"'
        print(response['Content-Disposition'])
        return response

    # Générer l'étiquette basée sur les données du fichier Excel
    def generate_label(self, data_row, qrcode, font_path, site):
        try:

            # Charger l'image de base pour l'étiquette
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'arcflash.png')
            label = Image.open(base_image_path)
            draw = ImageDraw.Draw(label)
            # Définir les polices
            font = ImageFont.truetype(font_path, 28)
            fontn = ImageFont.truetype(font_path, 50)
            fontd = ImageFont.truetype(font_path, 35)

            # Mappings pour les textes à afficher
            mappings = {
                (200, 740): f"{data_row['Unnamed: 2']} V",
                (180, 780): f"{data_row['Unnamed: 3']}",
                (220, 820): f"{data_row['Unnamed: 7']}",
                (185, 860): f"{data_row['Unnamed: 4']} mm",
                (170, 900): f"{data_row['Unnamed: 9']} Cal/cm²",
                (170, 940): f"{data_row['Unnamed: 5']} Cal/cm²",
                (185, 980): f"{data_row['Unnamed: 6']} mm",
                (210, 1020): f"{data_row['Unnamed: 8']} kA",
            }

            for position, text in mappings.items():
                draw.text(position, text, font=font, fill="black")

            processed_label = data_row['ArcFlash'].split('.', 1)[1]
            font_for_reper = get_font_for_text(processed_label, max_width=800, base_font_path=font_path,
                                               base_font_size=40)
            draw.text((500, 1095), f"{processed_label}", font=font_for_reper, fill="black")

            draw.text((1500, 1085), f"N: {data_row['Unnamed: 0']}", font=fontn, fill="black")
            draw.text((1420, 1015), "Septembre 2024", font=fontd, fill="black")

            # Coller le QR code généré sur l'image
            qr_img = Image.open(qrcode.image.path)
            qr_img = qr_img.resize((200, 200))
            label.paste(qr_img, (1430, 525))

            # Sauvegarder l'image dans un buffer et le retourner
            buffer = BytesIO()
            label.save(buffer, format="PNG")
            buffer.seek(0)  # Revenir au début du buffer
            # file_name = f"etiquette_{data_row['Unnamed: 0']}.png"
            file_name = f"arc_flash/{site.client.name}/{site.name}/etiquette_{data_row['Unnamed: 0']}.png"
            return ContentFile(buffer.getvalue(), file_name)
                               #f"arc_flash/{site.client.name}/{site.name}/etiquette_{data_row['Unnamed: 0']}.png")
        except Exception as e:
            print(f"Erreur lors de la génération de l'étiquette de levage : {e}")
            return None


    # Créer l'objet ArcFlashLabel
    def create_arcflash_label_object(self, data_row, site, qrcode, date, fichier, dossier):
        ArcFlashLabel.objects.create(
            cabinet_number=data_row['Unnamed: 0'],
            repere=data_row['ArcFlash'],
            network_voltage=data_row['Unnamed: 2'],
            gloves_class=data_row['Unnamed: 3'],
            protection_distance=data_row['Unnamed: 4'],
            max_energy=data_row['Unnamed: 9'],
            incident_energy=data_row['Unnamed: 5'],
            working_distance=data_row['Unnamed: 6'],
            ppe_category=data_row['Unnamed: 7'],
            ik3max=data_row['Unnamed: 8'],
            inspection_date=date,
            qrcode_id=qrcode.id,
            fichier=fichier,
            dossier=dossier,
            site=site,
        )
        return ArcFlashLabel.objects.last()


# Générer un code QR pour une étiquette
def generate_qr_code(uuid_value, site, numero):
    base_url = "https://kesafrica.com/report/"
    full_url = f"{base_url}{uuid_value}"
    qr = segno.make(full_url)
    qr_img = BytesIO()
    qr.save(qr_img, kind="png", scale=10, border=0)
    qr_filename = os.path.join(f"arc_flash/{site.client.name}/{site.name}/qr_code_{uuid_value}.png")
    qr_img.seek(0)
    qr_code = QRCode.objects.create(
        code=uuid_value,
        url=full_url,
        image=ContentFile(qr_img.getvalue(), qr_filename),
        numero=f"{site.client.name}_{site.name}_{numero}"
    )
    return qr_code




# Liste tous les ArcFlashLabels et permet de créer de nouveaux labels
class ArcFlashLabelListCreateView(generics.ListCreateAPIView):
    queryset = ArcFlashLabel.objects.all()
    serializer_class = ArcFlashLabelSerializer

# Récupère, met à jour ou supprime un ArcFlashLabel par son ID
class ArcFlashLabelRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ArcFlashLabel.objects.all()
    serializer_class = ArcFlashLabelSerializer
    lookup_field = 'uuid'  # Utilisation de uuid pour récupérer le label
