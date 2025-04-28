import locale
from datetime import datetime
import os
import sys
from PIL import Image


def resize_logo_for_template(input_image_path, coin_sup_gauche, coin_inf_droit):
    """
    Redimensionne une image logo pour qu'elle s'adapte aux coordonnées spécifiées
    tout en préservant son ratio d'aspect et sa transparence.

    Arguments:
        input_image_path (str): Chemin vers l'image d'entrée
        coin_sup_gauche (list): Coordonnées [x, y] du coin supérieur gauche
        coin_inf_droit (list): Coordonnées [x, y] du coin inférieur droit

    Retourne:
        Image: L'image PIL redimensionnée
    """
    try:
        # Coordonnées cibles pour le logo
        target_coords = {
            "Coin supérieur gauche": coin_sup_gauche,
            "Coin inférieur droit": coin_inf_droit,
        }

        # Calculer les dimensions cibles
        target_width = (
            target_coords["Coin inférieur droit"][0]
            - target_coords["Coin supérieur gauche"][0]
        )
        target_height = (
            target_coords["Coin inférieur droit"][1]
            - target_coords["Coin supérieur gauche"][1]
        )
        print(f"Dimensions cibles: {target_width}x{target_height} pixels")

        # Ouvrir l'image source
        img = Image.open(input_image_path)

        # Assurer que l'image a un canal alpha pour la transparence
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        print(f"Dimensions originales: {img.width}x{img.height} pixels")

        # Calculer le ratio d'aspect original
        original_ratio = img.width / img.height
        target_ratio = target_width / target_height

        # Déterminer les nouvelles dimensions en préservant le ratio
        if original_ratio > target_ratio:
            # L'image est plus large que l'espace cible
            new_width = target_width
            new_height = int(new_width / original_ratio)
        else:
            # L'image est plus haute que l'espace cible
            new_height = target_height
            new_width = int(new_height * original_ratio)

        # Si l'image redimensionnée reste trop grande pour la cible,
        # redimensionner à la plus petite dimension
        if new_width > target_width or new_height > target_height:
            if target_width / img.width < target_height / img.height:
                new_width = target_width
                new_height = int(new_width / original_ratio)
            else:
                new_height = target_height
                new_width = int(new_height * original_ratio)

        print(f"Nouvelles dimensions: {new_width}x{new_height} pixels")

        # Redimensionner l'image en préservant la transparence
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)

        # Créer une nouvelle image avec la taille cible (fond complètement transparent)
        final_img = Image.new(
            "RGBA", (target_width, target_height), (255, 255, 255, 255)
        )
        # Calculer la position pour centrer l'image redimensionnée
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2

        # Coller l'image redimensionnée avec son masque alpha
        final_img.paste(resized_img, (paste_x, paste_y), resized_img)
        # new_path = os.path.splitext(input_image_path)[0] + "_resized.png"
        # final_img.save(new_path, format="PNG")

        return final_img

    except Exception as e:
        print(f"Erreur lors du redimensionnement de l'image: {e}")
        # En cas d'erreur, on peut renvoyer l'image originale
        if "img" in locals():
            return img
        raise e


def format_date_range(start_date, end_date):
    """
    Formate une plage de dates pour afficher "du {jour1} au {jour2} {mois} {année}".

    :param start_date: Date de début au format "21 Novembre 2024"
    :param end_date: Date de fin au format "22 Novembre 2024"
    :return: Une chaîne formatée.
    """
    # Définir les paramètres régionaux en français
    try:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    except locale.Error:
        return "Erreur : Les paramètres régionaux français ne sont pas disponibles sur ce système."

    # Conversion des chaînes de dates en objets datetime
    start = datetime.strptime(start_date, "%d %B %Y")
    end = datetime.strptime(end_date, "%d %B %Y")

    # Vérification de l'année et du mois
    if start.year == end.year and start.month == end.month:
        return f"{start.day} et {end.day} {start.strftime('%B')} {start.year}"
    elif start.year == end.year:
        return f"du {start.day} {start.strftime('%B')} et {end.day} {end.strftime('%B')} {start.year}"
    else:
        return f"du {start.day} {start.strftime('%B')} {start.year} au {end.day} {end.strftime('%B')} {end.year}"


# Exemple d'utilisation
start_date = "21 Novembre 2024"
end_date = "22 Novembre 2024"
result = format_date_range(start_date, end_date)
print(result)  # Affiche: du 21 au 22 Novembre 2024
