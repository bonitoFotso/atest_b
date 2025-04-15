import os

from PIL import Image, ImageDraw, ImageFont
import json
from .data import load_data_from_excel
from django.conf import settings


def generate_habilitation_certificate(data, coordonnees_rectangles, output_path):
    # Ouvrir le modèle d'image
    try:
        img_file = os.path.join(settings.STATIC_ROOT, 'images', 'h1.png')

        img = Image.open(img_file)  # Assurez-vous que l'image est dans le même répertoire ou spécifiez le chemin correct
    except FileNotFoundError:
        print("Erreur : Le fichier 'h1.png' n'a pas été trouvé.")
        return

    # Créer un objet pour dessiner sur l'image
    draw = ImageDraw.Draw(img)

    # Parcourir les éléments à placer
    for nom_element, contenu in data.items():
        # Vérifier si les coordonnées pour cet élément existent
        if nom_element in coordonnees_rectangles:
            coords = coordonnees_rectangles[nom_element]
            # Obtenir les coordonnées du rectangle
            coin_sup_gauche = coords["Coin supérieur gauche"]
            coin_inf_droit = coords["Coin inférieur droit"]
            centre = coords["Centre"]

            # Calculer les dimensions du rectangle
            largeur_rect = coin_inf_droit[0] - coin_sup_gauche[0]
            hauteur_rect = coin_inf_droit[1] - coin_sup_gauche[1]

            # Vérifier si 'align' est spécifié, sinon utiliser 'top_left' par défaut
            align = contenu.get("align", "top_left")

            # Obtenir les décalages de position (0 par défaut)
            offset_x = contenu.get("offset_x", 0)
            offset_y = contenu.get("offset_y", 0)

            # Vérifier si l'élément est une image ou du texte
            if nom_element in ['Logo', 'Photo', 'QR Code', 'QR Code 2']:
                # Ouvrir l'image correspondante
                try:
                    image_element = Image.open(contenu["valeur"])  # contenu["valeur"] est le chemin vers l'image
                except FileNotFoundError:
                    print(f"Erreur : L'image '{contenu['valeur']}' n'a pas été trouvée pour '{nom_element}'.")
                    continue

                # Redimensionner l'image pour qu'elle s'adapte au rectangle
                image_element = image_element.resize((largeur_rect, hauteur_rect))

                # Calculer la position en fonction de l'alignement
                if align == "top_left":
                    position = (coin_sup_gauche[0] + offset_x, coin_sup_gauche[1] + offset_y)
                elif align == "center":
                    x = centre[0] - (largeur_rect // 2) + offset_x
                    y = centre[1] - (hauteur_rect // 2) + offset_y
                    position = (x, y)
                elif align == "left_center":
                    x = coin_sup_gauche[0] + offset_x
                    y = centre[1] - (hauteur_rect // 2) + offset_y
                    position = (x, y)
                else:
                    print(f"Alignement inconnu pour '{nom_element}', utilisation du coin supérieur gauche.")
                    position = (coin_sup_gauche[0] + offset_x, coin_sup_gauche[1] + offset_y)

                # Coller l'image sur le modèle
                img.paste(image_element, position)
            else:
                # C'est un élément texte
                valeur = contenu["valeur"]
                taille_police = contenu.get("taille_police", 20)  # Valeur par défaut si absent
                couleur = contenu.get("couleur", "black")  # Couleur par défaut en noir
                # Charger la police avec la taille spécifiée
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
                elif align == "center_vertical_center":
                    x = centre[0] - (text_width // 2) + offset_x
                    y = centre[1] - (text_height // 2) + offset_y
                else:
                    print(f"Alignement inconnu pour '{nom_element}', utilisation du coin supérieur gauche.")
                    x = coin_sup_gauche[0] + offset_x
                    y = coin_sup_gauche[1] + offset_y

                # Dessiner le texte
                draw.text((x, y), str(valeur), font=font, fill=couleur)
        else:
            print(f"Coordonnées non trouvées pour l'élément '{nom_element}'.")

    # Sauvegarder l'image générée
    img.save(output_path)


