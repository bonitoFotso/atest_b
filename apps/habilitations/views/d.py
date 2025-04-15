import pandas as pd
import segno
import os
import uuid


# Lire le fichier Excel
def read_excel(file_path):
    # Charger le fichier Excel
    df = pd.read_excel(file_path)
    # Retourner la colonne contenant les noms des QR codes (remplacer 'NomColonne' par le nom de votre colonne)
    return df['QR Code 2'].tolist()


# Générer les QR codes et les sauvegarder dans un dossier
def generate_qr_codes(names, output_folder, base_url):
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Pour chaque nom, générer un QR code
    for name in names:
        # Générer un UUID unique pour l'URL
        unique_id = str(uuid.uuid4())  # UUID sous forme de chaîne de caractères

        # Créer l'URL complète avec le nom et l'UUID
        url = f"{base_url}/{unique_id}"

        # Générer le QR code avec segno
        qr = segno.make(url)

        # Sauvegarder l'image du QR code
        qr_file_path = os.path.join(output_folder, f"{name}")
        qr.save(qr_file_path, scale=10, border=1)
        print(f"QR Code généré pour {name} avec UUID {unique_id} et sauvegardé sous {qr_file_path}")


# Chemin du fichier Excel et du dossier de sortie
excel_file = '2.xlsx'  # Remplacer par le chemin de votre fichier Excel
output_folder = 'generated_qr_codes'  # Dossier où les QR codes seront sauvegardés
base_url = 'www.kesafrica.com/media'  # Base URL pour générer l'URL complète

# Lire les noms des QR codes à partir du fichier Excel
names = read_excel(excel_file)

# Générer les QR codes
generate_qr_codes(names, output_folder, base_url)
