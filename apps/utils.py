# Function to dynamically adjust font size based on text length
from PIL import Image, ImageDraw, ImageFont


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


def draw_centered_text(draw, text, font, reference_point, fill="black"):
    """
    Dessine du texte centré par rapport à un point donné sur une image.

    :param draw: L'objet ImageDraw sur lequel dessiner le texte.
    :param text: Le texte à dessiner.
    :param font: L'objet ImageFont à utiliser pour le texte.
    :param reference_point: Un tuple (x, y) représentant le point de référence pour centrer le texte.
    :param fill: La couleur du texte (par défaut "black").
    """
    # Calculer la taille du texte avec textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculer la position pour centrer le texte
    text_x = reference_point[0] - (text_width // 2)  # Centrage horizontal par rapport au point de référence
    text_y = reference_point[1] - (text_height // 2)  # Centrage vertical si nécessaire (facultatif)

    # Dessiner le texte au centre par rapport au point de référence
    draw.text((text_x, text_y), text, font=font, fill=fill)