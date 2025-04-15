import os
import segno
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from apps.utils import draw_centered_text

# Configuration des chemins pour les images et polices
STATIC_ROOT = os.path.join(os.getcwd(), 'static')
OUTPUT_DIR = os.path.join(os.getcwd(), 'outputss')
QR_OUTPUT_DIR = os.path.join(os.getcwd(), 'qr')

if not os.path.exists(QR_OUTPUT_DIR):
    os.makedirs(QR_OUTPUT_DIR)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


# Générer le QR code
def generate_qr_code(numero):
    qr_url = numero
    qr = segno.make_qr(qr_url)

    qr_bytes = BytesIO()
    qr.save(qr_bytes, kind='png',border=0)

    qr_image_filename = os.path.join(QR_OUTPUT_DIR, f"qr_code_{numero}.png")
    with open(qr_image_filename, 'wb') as qr_file:
        qr_file.write(qr_bytes.getvalue())

    return qr_image_filename



def generate_etiquette_levage(qr_image_path, numero):
    try:
        # Charger l'image de base de l'étiquette
        et_image = Image.open('Extincteur.jpeg')

        # Charger l'image du QR code
        qr_image = Image.open(qr_image_path)
        qr_image = qr_image.resize((580, 580))

        # Positionner le QR code sur l'image de l'étiquette
        et_image.paste(qr_image, (et_image.width - qr_image.width - 1130, et_image.height - qr_image.height - 970))

        # Ajouter le texte
        draw = ImageDraw.Draw(et_image)
        font = ImageFont.truetype('ARIALBD.TTF', 70)

        # Point de référence pour le centrage du texte (exemple : 2070, 1475)
        reference_point = (2180, 1490)
        text = f"{numero}"

        # Utiliser la fonction réutilisable pour dessiner le texte centré
        draw_centered_text(draw, text, font, reference_point, fill="blue")

        # Sauvegarder l'image d'étiquette finale
        output_filename = os.path.join(OUTPUT_DIR, f"etiquette_extincteur_{numero}.png")
        et_image.save(output_filename)

        print(f"Étiquette {numero} générée avec succès : {output_filename}")
        return output_filename

    except Exception as e:
        print(f"Erreur lors de la génération de l'étiquette levage : {e}")
        return None


# Fonction principale pour générer plusieurs étiquettes
def generate_multiple_etiquettes(num_etiquettes):
    for numero in range(1, num_etiquettes + 1):
        qr_image_path = generate_qr_code(numero)
        generate_etiquette_levage(qr_image_path, numero)


# Entré utilisateur pour spécifier le nombre d'étiquettes à générer
if __name__ == "__main__":
    num_etiquettes = 1
    generate_multiple_etiquettes(num_etiquettes)
