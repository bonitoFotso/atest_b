import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import ast  # Pour analyser les clés encodées comme des listes dans des chaînes


def get_coordinates_for_element(nom_element, coordonnees_rectangles):
    """Retourne les coordonnées associées à un élément donné."""
    for encoded_key, coords in coordonnees_rectangles.items():
        key_list = ast.literal_eval(encoded_key)  # Convertir la clé encodée en liste
        if key_list[0] == nom_element:  # Vérifie si la première partie de la clé correspond
            return coords
    return None  # Retourne None si l'élément n'est pas trouvé


def place_image(draw, img, nom_element, coords, contenu, align, offset_x, offset_y):
    """Place une image sur l'image modèle en fonction des coordonnées et de l'alignement."""
    try:
        img_f = os.path.join(settings.STATIC_ROOT, 'images', 'photos', contenu["valeur"])
        image_element = Image.open(img_f)
    except FileNotFoundError:
        print(f"Erreur : L'image '{contenu['valeur']}' n'a pas été trouvée pour '{nom_element}'.")
        return

    # Obtenir les dimensions du rectangle
    coin_sup_gauche = coords["Coin supérieur gauche"]
    coin_inf_droit = coords["Coin inférieur droit"]
    largeur_rect = coin_inf_droit[0] - coin_sup_gauche[0]
    hauteur_rect = coin_inf_droit[1] - coin_sup_gauche[1]

    # Redimensionner l'image pour qu'elle s'adapte au rectangle
    image_element = image_element.resize((largeur_rect, hauteur_rect))

    # Calculer la position en fonction de l'alignement
    centre = coords["Centre"]
    if align == "top_left":
        position = (coin_sup_gauche[0] + offset_x, coin_sup_gauche[1] + offset_y)
    elif align == "top_center":
        position = (centre[0] - (largeur_rect // 2) + offset_x, coin_sup_gauche[1] + offset_y)
    elif align == "center_vertical_left":
        position = (coin_sup_gauche[0] + offset_x, centre[1] + offset_y)
    elif align == "center":
        position = (centre[0] - (largeur_rect // 2) + offset_x, centre[1] - (hauteur_rect // 2) + offset_y)
    elif align == "left_center":
        position = (coin_sup_gauche[0] + offset_x, centre[1] - (hauteur_rect // 2) + offset_y)
    else:
        print(f"Alignement inconnu pour '{nom_element}', utilisation du coin supérieur gauche.")
        position = (coin_sup_gauche[0] + offset_x, coin_sup_gauche[1] + offset_y)

    # Coller l'image sur le modèle
    img.paste(image_element, position)


def place_text(draw, img, nom_element, coords, contenu, align, offset_x, offset_y):
    """Place du texte sur l'image modèle en fonction des coordonnées et de l'alignement."""
    valeur = contenu["valeur"]
    taille_police = contenu.get("taille_police", 20)  # Valeur par défaut si absent
    couleur = contenu.get("couleur", "black")  # Couleur par défaut en noir

    try:
        font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')
        font = ImageFont.truetype(font_path, taille_police)  # Assurez-vous que la police est disponible
    except IOError:
        print("Erreur : La police 'ABD.TTF' n'a pas été trouvée. Utilisation de la police par défaut.")
        font = ImageFont.load_default()

    # Mesurer la taille du texte en utilisant font.getbbox()
    bbox = font.getbbox(str(valeur))
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculer la position en fonction de l'alignement
    coin_sup_gauche = coords["Coin supérieur gauche"]
    centre = coords["Centre"]
    if align == "top_left":
        x = coin_sup_gauche[0] + offset_x
        y = coin_sup_gauche[1] + offset_y
    elif align == "center":
        x = centre[0] - (text_width // 2) + offset_x
        y = centre[1] - (text_height // 2) + offset_y
    elif align == "left_center":
        x = coin_sup_gauche[0] + offset_x
        y = centre[1] - (text_height // 2) + offset_y
    elif align == "center_vertical_left":
        x = coin_sup_gauche[0] + offset_x
        y = centre[1] - (text_height // 2) + offset_y
    else:
        print(f"Alignement inconnu pour '{nom_element}', utilisation du coin supérieur gauche.")
        x = coin_sup_gauche[0] + offset_x
        y = coin_sup_gauche[1] + offset_y

    # Dessiner le texte
    draw.text((x, y), str(valeur), font=font, fill=couleur)


def generate_habilitation_certificate(data, coordonnees_rectangles, output_path):
    """Génère un certificat d'habilitation à partir des données et des coordonnées."""
    try:
        img_file = os.path.join(settings.STATIC_ROOT, 'images', 'he2.png')
        img = Image.open(img_file)  # Assurez-vous que l'image est dans le bon répertoire ou spécifiez le chemin correct
    except FileNotFoundError:
        print("Erreur : Le fichier 'he2.png' n'a pas été trouvé.")
        return

    # Créer un objet pour dessiner sur l'image
    draw = ImageDraw.Draw(img)

    # Parcourir les éléments à placer
    for nom_element, contenu in data.items():
        # Trouver les coordonnées correspondant à l'élément
        coords = get_coordinates_for_element(nom_element, coordonnees_rectangles)

        if coords:
            print(f"Nom de l'élément : {nom_element}")
            align = contenu.get("align", "top_left")
            offset_x = contenu.get("offset_x", 0)
            offset_y = contenu.get("offset_y", 0)

            # Vérifier si l'élément est une image ou du texte
            if nom_element in ['Logo', 'Photo', 'QR', 'QR 2']:
                place_image(draw, img, nom_element, coords, contenu, align, offset_x, offset_y)
            else:
                place_text(draw, img, nom_element, coords, contenu, align, offset_x, offset_y)
        else:
            print(f"Coordonnées non trouvées pour l'élément '{nom_element}'.")

    # Sauvegarder l'image générée
    img.save(output_path)
