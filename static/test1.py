from PIL import Image, ImageDraw, ImageFont


def draw_text_in_rectangle(image_path, output_path, text, coords, font_path):
    # Charger l'image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Récupérer les coordonnées du rectangle
    x1, y1 = coords["Coin supérieur gauche"]
    x2, y2 = coords["Coin inférieur droit"]
    rect_width = x2 - x1
    rect_height = y2 - y1

    # Taille de police de départ
    font_size = 100  # Taille initiale pour calculer la taille optimale
    font = ImageFont.truetype(font_path, font_size)

    # Adapter la taille de la police pour le texte dans le rectangle
    while True:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if text_width <= rect_width and text_height <= rect_height:
            break
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        if font_size <= 10:  # Taille minimale pour ne pas descendre trop bas
            break

    # Découper le texte en lignes si nécessaire
    lines = []
    words = text.split()
    line = ""
    for word in words:
        # Test si l'ajout d'un mot fait dépasser la largeur du rectangle
        test_line = line + ("" if line == "" else " ") + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]
        if test_width <= rect_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    lines.append(line)

    # Ajuster si le texte est trop long pour le rectangle, au cas où
    while True:
        bbox = draw.textbbox((0, 0), "\n".join(lines), font=font)
        text_height = bbox[3] - bbox[1]
        if text_height <= rect_height:
            break
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)

    # Calculer la position pour centrer le texte dans le rectangle
    y_text = y1 + (rect_height - text_height) // 2

    # Dessiner le texte
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_text = x1 + (rect_width - text_width) // 2
        draw.text((x_text, y_text), line, font=font, fill="black")
        y_text += bbox[3] - bbox[1]

    # Sauvegarder l'image avec le texte
    image.save(output_path)


# Exemple d'utilisation
font_path="fonts/arial.ttf"

image_path = "json/h1.png"
output_path = "output_image.jpg"
text = "Votre texte très long à insérer dans le rectangleje veux un script pyton qui prend en entre le coordonne d'un rectangle sur une image et du texte puis ecris se texte dans le rectangle sur l'image et si le texte est plus long que la longueur du rectancle le texte doit continuer sur la ligne s "
coords = {
    "Coin supérieur gauche": [274, 373],
    "Coin supérieur droit": [693, 373],
    "Coin inférieur gauche": [274, 407],
    "Coin inférieur droit": [693, 407],
    "Centre": [483, 390]
}
draw_text_in_rectangle(image_path, output_path, text, coords, font_path)

# Exemple d'utilisation
#font_path="fonts/arial.ttf"
#image_path = "images/h1.png"
#output_path = "output_image.jpg"
#text = "Votre texte très long à insérer dans le rectangleje veux un script pyton qui prend en entre le coordonne d'un rectangle sur une image et du texte puis ecris se texte dans le rectangle sur l'image et si le texte est plus long que la longueur du rectancle le texte doit continuer sur la ligne suivante et si je texte est plus grand que le rectangle le script modifier la taille des caracter afin que le texte s'ecrive dans le rectangle sans deborder "
#rectangle = (50, 50, 400, 200)  # Coordonnées du rectangle (x1, y1, x2, y2)
#draw_text_in_rectangle(image_path, output_path, text, rectangle, font_path)
