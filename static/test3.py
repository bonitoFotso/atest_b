from PIL import Image, ImageDraw, ImageFont
import re


def parse_text_segments(text):
    segments = []

    # Expressions régulières pour détecter les balises de formatage
    bold_pattern = r'\*\*(.*?)\*\*'
    color_pattern = r'\{(.*?)\|(.*?)\}'

    # Analyser les segments en gras
    last_end = 0
    for bold_match in re.finditer(bold_pattern, text):
        if bold_match.start() > last_end:
            segments.append({"text": text[last_end:bold_match.start()], "bold": False, "color": "black"})
        segments.append({"text": bold_match.group(1), "bold": True, "color": "black"})
        last_end = bold_match.end()
    text = text[last_end:]  # Reste du texte après les segments en gras

    # Analyser les segments en couleur
    last_end = 0
    for color_match in re.finditer(color_pattern, text):
        if color_match.start() > last_end:
            segments.append({"text": text[last_end:color_match.start()], "bold": False, "color": "black"})
        segments.append({"text": color_match.group(1), "bold": False, "color": color_match.group(2)})
        last_end = color_match.end()
    if last_end < len(text):
        segments.append({"text": text[last_end:], "bold": False, "color": "black"})

    return segments


def draw_text_in_rectangle(image_path, output_path, text, coords, font_path="arial.ttf", initial_font_size=20):
    # Charger l'image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Récupérer les coordonnées du rectangle
    x1, y1 = coords["Coin supérieur gauche"]
    x2, y2 = coords["Coin inférieur droit"]
    rect_width = x2 - x1
    rect_height = y2 - y1

    # Analyser les segments de texte avec formatage
    segments = parse_text_segments(text)

    # Ajuster la taille de la police pour faire tenir le texte dans le rectangle
    font_size = initial_font_size
    while True:
        font = ImageFont.truetype(font_path, font_size)
        bold_font = ImageFont.truetype(font_path, font_size + 2)  # Police pour le gras

        # Préparer les lignes de texte
        lines = []
        current_line = []
        current_width = 0

        for segment in segments:
            segment_font = bold_font if segment["bold"] else font
            color = segment["color"]

            # Mesurer la largeur de chaque segment et décider si on doit couper la ligne
            segment_width = draw.textlength(segment["text"], font=segment_font)
            if current_width + segment_width <= rect_width:
                current_line.append((segment["text"], segment_font, color))
                current_width += segment_width
            else:
                lines.append(current_line)
                current_line = [(segment["text"], segment_font, color)]
                current_width = segment_width

        lines.append(current_line)

        # Calculer la hauteur totale requise
        total_text_height = 0
        for line in lines:
            max_height = 0
            for segment_text, segment_font, _ in line:
                bbox = draw.textbbox((0, 0), segment_text, font=segment_font)
                max_height = max(max_height, bbox[3] - bbox[1])
            total_text_height += max_height

        # Vérifier si le texte tient dans le rectangle
        if total_text_height <= rect_height:
            break  # La police actuelle convient
        else:
            font_size -= 1  # Réduire la taille de la police

    # Dessiner le texte ligne par ligne
    current_y = y1
    for line in lines:
        current_x = x1
        for segment_text, segment_font, color in line:
            draw.text((current_x, current_y), segment_text, font=segment_font, fill=color)
            bbox = draw.textbbox((0, 0), segment_text, font=segment_font)
            current_x += bbox[2] - bbox[0]  # Avancer pour le prochain segment
        current_y += max(bbox[3] - bbox[1] for _, _, _ in line)  # Ajouter la hauteur de ligne

    # Sauvegarder l'image
    image.save(output_path)


# Exemple d'utilisation
font_path = "fonts/arial.ttf"
image_path = "json/h1.png"
output_path = "output/formatted_text_image.jpg"
text = "Voici un **texte en gras** et {texte en couleur|red} normal."
coords = {
    "Coin supérieur gauche": [274, 373],
    "Coin supérieur droit": [693, 373],
    "Coin inférieur gauche": [274, 407],
    "Coin inférieur droit": [693, 407],
    "Centre": [483, 390]
}

draw_text_in_rectangle(image_path, output_path, text, coords, font_path)
