from datetime import datetime
import segno
from uuid import uuid4
import os

from apps.documents.models import QRCode


def generate_qrcode(title, output_dir="qrcodes"):
    """
    Génère un QR code à partir d'un UUID et d'un titre d'habilitation avec Segno.

    Args:
        title (str): Le titre de l'habilitation.
        output_dir (str): Répertoire où enregistrer les QR codes.

    Returns:
        str: Chemin du fichier QR code généré.
    """
    # Créer un UUID unique
    unique_id = str(uuid4())

    # Texte à encoder dans le QR code
    qr_data = f"https://kesdocs.vercel.app/attestation/{unique_id}"

    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Nom du fichier de sortie
    output_file = os.path.join(output_dir, f"{unique_id}.png")

    # Générer le QR code
    qr = segno.make(qr_data)
    qr.save(output_file, scale=10)

    QRCode.objects.create(code=unique_id, image=output_file, url=qr_data, numero=title)
    file = QRCode.objects.get(code=unique_id)
    print(f"QR code généré : {file.image.path}")
    return file.image.path


def generate_title_number(prefix="KES/F", site="YDE/SABC", index=1):
    """
    Génère un numéro de titre unique.

    Args:
        prefix (str): Le préfixe du numéro de titre, par exemple "KES/FORMATION".
        site (str): La localisation ou le site, par exemple "YDE/SABC".
        index (int): L'index incrémental, par exemple 1, 2, 3...

    Returns:
        str: Numéro de titre formaté.
    """
    # Obtenir le mois et l'année actuels
    now = datetime.now()
    month = now.strftime("%m")
    year = now.strftime("%y")

    # Construire le numéro de titre
    title_number = f"{prefix}/TH/{site}/{month}/{year}-{index}"
    return title_number
