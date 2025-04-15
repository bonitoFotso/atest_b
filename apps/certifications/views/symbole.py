import os

from PIL import Image, ImageDraw, ImageFont

# Dictionnaire des rôles et niveaux de tension associés aux symboles
symbol_mapping = {
    "B0": {"tension": "BT", "role": "Travaux non électriques ou au voisinage", "domaine": "BT"},
    "H0": {"tension": "HT", "role": "Travaux non électriques ou au voisinage", "domaine": "HT"},
    "H0V": {"tension": "HT", "role": "Travaux non électriques ou au voisinage (voisinage HT)", "domaine": "HT"},
    "B1": {"tension": "BT", "role": "Exécutant, Chargé d’intervention", "domaine": "BT"},
    "B1V": {"tension": "BT", "role": "Exécutant, Chargé d’intervention (voisinage BT)", "domaine": "BT"},
    "B2": {"tension": "BT", "role": "Chargé de travaux", "domaine": "BT"},
    "B2V": {"tension": "BT", "role": "Chargé de travaux (voisinage BT)", "domaine": "BT"},
    "B2V Essais": {"tension": "BT", "role": "Chargé de travaux pour essais", "domaine": "BT"},
    "BC": {"tension": "BT", "role": "Chargé de consignation en BT", "domaine": "BT"},
    "BR": {"tension": "BT ou HT", "role": "Chargé d’interventions de dépannage et de maintenance",
           "domaine": "BT et HT"},
    "BE": {"tension": "BT ou HT",
           "role": "Chargé d’opérations spécifiques (Essais, Vérifications, Mesurages, Manœuvres)",
           "domaine": "BT et HT"},
    "H1": {"tension": "HT", "role": "Exécutant, Chargé d’intervention", "domaine": "HT"},
    "H1V": {"tension": "HT", "role": "Exécutant, Chargé d’intervention (voisinage HT)", "domaine": "HT"},
    "H2": {"tension": "HT", "role": "Chargé de travaux", "domaine": "HT"},
    "H2V": {"tension": "HT", "role": "Chargé de travaux (voisinage HT)", "domaine": "HT"},
    "H2V Essais": {"tension": "HT", "role": "Chargé de travaux pour essais (voisinage HT)", "domaine": "HT"},
    "HC": {"tension": "HT", "role": "Chargé de consignation en HT", "domaine": "HT"}
}


def organize_by_roles(symbols):
    roles = {
        "Exécutant": {"symbole": [], "tension": []},
        "Chargé de travaux": {"symbole": [], "tension": []},
        "Chargé d’intervention": {"symbole": [], "tension": []},
        "Chargé d’opérations spécifiques": {"symbole": [], "tension": []},
        "Travaux non électriques ou au voisinage": {"symbole": [], "tension": []},
        "Chargé de consignation": {"symbole": [], "tension": []}
    }

    # Parcours des symboles
    for symbol in symbols:
        if symbol in symbol_mapping:
            role = symbol_mapping[symbol]["role"]
            tension = symbol_mapping[symbol]["tension"]

            # Associer chaque symbole au rôle correspondant
            for key in roles:
                if key in role:  # Si le rôle contient le mot-clé
                    roles[key]["symbole"].append(symbol)
                    # Ajouter la tension si elle n'est pas déjà présente pour ce rôle
                    if tension not in roles[key]["tension"]:
                        roles[key]["tension"].append(tension)

    # Supprimer les rôles sans symboles associés
    roles = {key: value for key, value in roles.items() if value["symbole"]}

    return roles

def create_image(content_list, output_path):
    """Generate an image with the given content list and title."""
    img_width, img_height = 400, 300
    background_color = "white"
    text_color = "black"

    # Create a blank image
    img = Image.new("RGB", (img_width, img_height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Define font and text properties
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        title_font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()

    # Add content
    y_position = 8
    for item in content_list:
        draw.text((5, y_position), item, fill=text_color, font=font)
        y_position += 30

    # Save the image
    img.save(output_path)

def generate_img(roles_results,participant):
    roles_list = [f"{role}" for role, details in roles_results.items()]
    create_image(roles_list, f"{participant}_roles_image.png")

    symbols = [f"{', '.join(details['symbole'])}" for role, details in roles_results.items()]
    create_image(symbols, f"{participant}_symbols_image.png")

    tensions = [f"{', '.join(details['tension'])}" for role, details in roles_results.items()]
    create_image(tensions, f"{participant}_tensions_image.png")

# Load the Excel file and sheet

# Step 1: Extract relevant data

symbols_to_analyze = ["B0", "H0", "H0V", "B1", "B1V", "B2", "B2V", "BC", "BR", "H1", "H1V", "H2", "H2V", "HC"]


def generate_images_per_category(df, output_dir):
    """
    Generate three separate images per participant: one for roles, one for symbols, and one for tension domains.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for _, row in df.iterrows():
        participant_name = f"{row['Nom']} {row['Prenom']}".strip()
        if participant_name == "NOMS PRENOMS" or not participant_name:
            continue  # Skip invalid entries

        sanitized_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in participant_name)

        # Filter roles, symbols, and tension domains where "APTE"
        symbols = [symbol for symbol in symbols_to_analyze if row.get(f"{symbol}", "") == "APTE"]

        # print(symbols)
        roles_results = organize_by_roles(symbols)

        # Create an image for each category
        generate_img(roles_results, sanitized_name)

        print(roles_results)



# Generate the images

