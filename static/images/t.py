import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


def generate_etiquette(qr_image_path, numero, client_name, site_name, base_image_path, qr_size):
    """
    Génère une étiquette en superposant un QR code à une image de base et en ajoutant des informations textuelles.

    :param qr_image_path: Chemin de l'image du QR code.
    :param numero: Numéro de l'étiquette.
    :param client_name: Nom du client.
    :param site_name: Nom du site.
    :param base_image_path: Chemin de l'image de base pour l'étiquette.
    :param qr_size: Taille à laquelle redimensionner l'image du QR code.
    :return: L'image générée sous forme de fichier.
    """
    try:
        # Charger l'image de base de l'étiquette
        et_image = Image.open(base_image_path)

        # Charger et ajuster la taille du QR code
        qr_image = Image.open(qr_image_path)
        qr_image = qr_image.resize(qr_size)
        et_image.paste(qr_image, (et_image.width - qr_image.width - 140, et_image.height - qr_image.height - 430))

        # Ajouter le texte
        draw = ImageDraw.Draw(et_image)
        font = ImageFont.truetype("arial.ttf", 20, encoding="lat1")
        font2 = ImageFont.truetype("arial.ttf", 35, encoding="unic")

        # Texte personnalisé
        # draw.text((200, 112), f"{client_name} {site_name} {numero}", font=font, fill="black")
        draw.text((690, 370), f"KES_VERIF_THERMO_{numero}",font=font, fill="black")
        draw.text((780, 680), f"{numero}", font=font2, fill="black")

        # Sauvegarder l'image dans un buffer
        buffer = BytesIO()
        et_image.save(buffer, format="PNG")
        buffer.seek(0)

        # Retourner l'image sous forme de fichier
        file_name = f"etiquette_{numero}_with_qrcode.png"
        return ContentFile(buffer.getvalue(), file_name)

    except Exception as e:
        print(f"Erreur lors de la génération de l'étiquette {os.path.basename(base_image_path).split('.')[0]} : {e}")
        return None

qr_image_path = 'qr.png'  # Le chemin vers votre QR code
base_image_path = 'thermographique.jpeg'  # Le chemin de l'image de base pour l'étiquette
client_name = 'Nom du Client'
site_name = 'Nom du Site'
numero = 1230  # Numéro de l'étiquette

# Générer l'étiquette
etiquette_image = generate_etiquette(qr_image_path, numero, client_name, site_name, base_image_path, (230, 230))

# Sauvegarder ou traiter l'image générée
if etiquette_image:
    with open('output_etiquette4.png', 'wb') as f:
        f.write(etiquette_image.read())
    print("L'étiquette a été générée avec succès.")