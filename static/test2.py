from PIL import Image, ImageDraw, ImageFont
import os

def draw_text_in_rectangle(image_path, output_path, text_segments, coords, font_path="arial.ttf"):
    # Charger l'image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Récupérer les coordonnées du rectangle
    x1, y1 = coords["Coin supérieur gauche"]
    x2, y2 = coords["Coin inférieur droit"]
    rect_width = x2 - x1
    rect_height = y2 - y1

    # Position de départ pour le texte
    current_x = x1
    current_y = y1

    # Écrire chaque segment de texte, en allant à la ligne si nécessaire
    for segment in text_segments:
        text = segment["text"]
        font_size = segment.get("font_size", 30)
        color = segment.get("color", "black")

        # Charger la police avec la taille spécifiée
        font = ImageFont.truetype(font_path, font_size)

        # Diviser le texte en mots pour gestion ligne par ligne
        words = text.split()
        line = ""

        for word in words:
            test_line = f"{line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Si le texte dépasse la largeur, on le dessine et passe à la ligne suivante
            if current_x + text_width > x2:
                draw.text((current_x, current_y), line, font=font, fill=color)
                current_y += text_height  # Descendre à la ligne suivante
                line = word  # Commencer une nouvelle ligne avec le mot actuel
                current_x = x1  # Revenir à la marge gauche
            else:
                line = test_line  # Sinon, ajouter le mot à la ligne actuelle

        # Dessiner la dernière ligne du segment s'il en reste
        if line:
            draw.text((current_x, current_y), line, font=font, fill=color)
            current_y += text_height  # Passer à la ligne suivante pour le prochain segment
            current_x = x1  # Revenir à la marge gauche pour le prochain segment

        # Vérifier si on dépasse le rectangle en hauteur
        if current_y > y2:
            break  # Arrêter si on dépasse la hauteur du rectangle

    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Sauvegarder l'image avec le texte
    image.save(output_path)

# Exemple d'utilisation
font_path = "fonts/arial.ttf"
image_path = "json/h1.png"
output_path = "output/output_image.jpg"
text_segments = [
    {"text": "Voici un ", "font_size": 20, "color": "blue"},
    {"text": "texte important", "font_size": 25, "color": "red"},
    {"text": " avec différents styles.", "font_size": 20, "color": "black"}
]
coords = {
    "Coin supérieur gauche": [274, 373],
    "Coin supérieur droit": [693, 373],
    "Coin inférieur gauche": [274, 407],
    "Coin inférieur droit": [693, 407],
    "Centre": [483, 390]
}
draw_text_in_rectangle(image_path, output_path, text_segments, coords, font_path)
