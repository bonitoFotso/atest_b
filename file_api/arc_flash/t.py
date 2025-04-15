import os
import zipfile
import uuid
import segno
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse
from django.views import View
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from file_api.models import ArcFlashLabel, QRCode, Site, Dossier, Fichier, \
    Etiquette  # Assurez-vous que le modèle est bien importé


class GenerateArcFlashLabelsView(View):
    def post(self, request, *args, **kwargs):
        # Vérifiez que le fichier est fourni dans la requête
        site_id = request.POST.get('site')
        excel_file = request.FILES.get('file')
        date_ins = request.POST.get('date')

        if not excel_file or not site_id:
            return HttpResponse("Aucun fichier ou site fourni", status=400)

        try:
            site_obj = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            return HttpResponse("Site non trouvé", status=404)

        # Charger les données depuis le fichier Excel
        df = pd.read_excel(excel_file, sheet_name='Export')  # Modifier le nom de la feuille selon le fichier
        font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')

        # Charger l'image de base pour l'étiquette
        base_image_path = os.path.join(settings.MEDIA_ROOT, 'arcflash.png')  # Modifier selon votre template
        base_image = Image.open(base_image_path)

        # Préparer le fichier ZIP
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:

            # Parcourir chaque ligne du fichier Excel pour générer des étiquettes
            for i, row in df.iterrows():
                try:
                    qrcode = generate_qr_code(uuid.uuid4(), site_obj, row['Unnamed: 0'])
                    # Générer l'étiquette Arc Flash
                    output_image = self.generate_label(row, base_image, qrcode, font_path,)

                    # creer ou obtenir les dossiers
                    dossier_annee, _ = Dossier.objects.get_or_create(nom=str(qrcode.created_at.year), parent = None )
                    dossier_rapports, _ = Dossier.objects.get_or_create(nom='rapports', parent=dossier_annee)
                    dossier_client, _ = Dossier.objects.get_or_create(name=site_obj.client.name, parent=dossier_rapports)
                    dossier_site, _ = Dossier.objects.get_or_create(name=site_obj.name, parent=dossier_client)
                    dossier_type_inspection, _ = Dossier.objects.get_or_create(name="ArcFlash", parent=dossier_site)
                    dossier_numero_rapport, _ = Dossier.objects.get_or_create(name=qrcode.numero, parent=dossier_type_inspection)
                    fichier_etiquette, _ = Fichier.objects.get_or_create(name=qrcode.numero, dossier=dossier_numero_rapport,
                                                                         fichier=output_image,
                                                                         type='Etiquette')
                    fichier_qr, _ = Fichier.objects.get_or_create(name=qrcode.numero, dossier=dossier_numero_rapport,
                                                                  fichier=qrcode.image, type='QRCode' )
                    etiquette = self.creat_arc_etiquette(site_obj,"ArcFlash",date_ins,qrcode.numero,output_image,True)
                    acr = self.create_arcflash_label_object(row, site_obj, qrcode,date_ins, etiquette, fichier_etiquette, dossier_numero_rapport)

                    # Ajouter l'étiquette au fichier ZIP
                    if acr.fichier:
                        zip_file.writestr(f"etiquette_{row['Unnamed: 0']}.png", acr.fichier.read())


                except Exception as e:
                    print(f"Erreur lors du traitement de la ligne {i}: {e}")

        # Préparer la réponse ZIP
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="etiquettes_arcflash.zip"'
        return response


    # Define a function to generate labels based on the Excel data
    def generate_label(self,data_row, label_image, qr_img, font_path):
        label = label_image.copy()
        draw = ImageDraw.Draw(label)

        font = ImageFont.truetype(font_path, 28)
        fontn = ImageFont.truetype(font_path, 50)
        fontd = ImageFont.truetype(font_path, 35)

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
        font_for_reper = get_font_for_text(processed_label, max_width=800, base_font_path=font_path, base_font_size=40)
        draw.text((500, 1095), f"{processed_label}", font=font_for_reper, fill="black")

        draw.text((1500, 1085), f"N: {data_row['Unnamed: 0']}", font=fontn, fill="black")
        draw.text((1420, 1015), "Septembre 2024", font=fontd, fill="black")

        qr_img = qr_img.resize((200, 200))
        label.paste(qr_img, (1430, 525))
        buffer = BytesIO()
        label.save(buffer, format="PNG")
        file_name = f"etiquette_{data_row['Unnamed: 0']}.png"
        return ContentFile(buffer.getvalue(), file_name)

    def create_arcflash_label_object(self, data_row, site, qrcode, date, etiquette, fichier,dossier):
        """ Crée un objet ArcFlashLabel dans la base de données """
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
            etiquette=etiquette

        )
        return ArcFlashLabel.objects.last()

    def creat_arc_etiquette(self,site,inspectiontype,date,numero,image,isAssigned):
        etiquette = Etiquette.objects.create(
            site=site,
            inspectionType=inspectiontype,
            date=date,
            numero=numero,
            image=image,
            isAssigned=isAssigned,
        )
        return etiquette


# Define a function to generate QR code
def generate_qr_code(uuid_value,site,numero):
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


# Define a function to dynamically adjust the font size based on text length
def get_font_for_text(text, max_width, base_font_path, base_font_size):
    font = ImageFont.truetype(base_font_path, base_font_size)
    temp_image = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(temp_image)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    while text_width > max_width and base_font_size > 10:
        base_font_size -= 2
        font = ImageFont.truetype(base_font_path, base_font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

    return font


# Define a function to generate labels based on the Excel data
def generate_label(data_row, label_image, font_path):
    label = label_image.copy()
    draw = ImageDraw.Draw(label)

    font = ImageFont.truetype(font_path, 28)
    fontn = ImageFont.truetype(font_path, 50)
    fontd = ImageFont.truetype(font_path, 35)

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
    font_for_reper = get_font_for_text(processed_label, max_width=800, base_font_path=font_path, base_font_size=40)
    draw.text((500, 1095), f"{processed_label}", font=font_for_reper, fill="black")

    draw.text((1500, 1085), f"N: {data_row['Unnamed: 0']}", font=fontn, fill="black")
    draw.text((1420, 1015), "Septembre 2024", font=fontd, fill="black")

    new_uuid = str(uuid.uuid4())
    qr_img = generate_qr_code(new_uuid)
    qr_img = qr_img.resize((200, 200))
    label.paste(qr_img, (1430, 525))

    return label, new_uuid


# View to handle the Excel upload and generate ArcFlash labels
class UploadArcFlashView(View):
    def post(self, request, *args, **kwargs):
        # Get the uploaded Excel file from the request
        excel_file: UploadedFile = request.FILES.get('file')

        if not excel_file:
            return HttpResponse("No file uploaded", status=400)

        try:
            # Load the Excel file
            df = pd.read_excel(excel_file, sheet_name='Export')

            # Load the base image for labels
            label_image_path = os.path.join(os.path.dirname(__file__), 'arcflash.png')
            label_image = Image.open(label_image_path)

            font_path = os.path.join(os.path.dirname(__file__), 'ARIALBD.TTF')

            # Create an in-memory zip file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                # Loop through each row in the DataFrame and generate labels
                for i in range(len(df)):
                    data_row = df.iloc[i]
                    label, uuid_generated = generate_label(data_row, label_image, font_path)

                    # Save each label to the zip
                    label_img_bytes = BytesIO()
                    label.save(label_img_bytes, format="JPEG")
                    label_img_bytes.seek(0)

                    zip_file.writestr(f"AF_{data_row['Unnamed: 0']}_label.jpg", label_img_bytes.read())

            # Set the correct file pointer
            zip_buffer.seek(0)

            # Return the zip file as a response
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="arcflash_labels.zip"'
            return response

        except Exception as e:
            return HttpResponse(f"Error processing file: {str(e)}", status=500)
