import os
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import ast
from pathlib import Path
import segno  # Ajout de l'import pour segno
import io

from apps.habilitations.utils import resize_logo_for_template  # Nécessaire pour convertir le QR code en image PIL

# Configure logging
logger = logging.getLogger(__name__)


class CertificateGenerationError(Exception):
    """Custom exception for certificate generation errors."""

    pass


def parse_coordinates_key(encoded_key: str) -> List[str]:
    """
    Safely parse an encoded key string into a list.

    Args:
        encoded_key: String representation of a list

    Returns:
        Parsed list of strings

    Raises:
        ValueError: If the key cannot be parsed correctly
    """
    try:
        return ast.literal_eval(encoded_key)
    except (SyntaxError, ValueError) as e:
        logger.error(f"Failed to parse coordinates key: {encoded_key}")
        raise ValueError(f"Invalid coordinates key format: {encoded_key}") from e


def get_coordinates_for_element(
    nom_element: str, coordonnees_rectangles: Dict[str, Dict[str, Tuple[int, int]]]
) -> Optional[Dict[str, Tuple[int, int]]]:
    """
    Return the coordinates associated with a given element.

    Args:
        nom_element: Element name to search for
        coordonnees_rectangles: Dictionary mapping encoded keys to coordinate dictionaries

    Returns:
        Coordinate dictionary or None if not found
    """
    if not coordonnees_rectangles:
        logger.warning("Empty coordinates dictionary provided")
        return None

    try:
        for encoded_key, coords in coordonnees_rectangles.items():
            key_list = parse_coordinates_key(encoded_key)
            if key_list and key_list[0] == nom_element:
                return coords
    except Exception as e:
        logger.error(f"Error finding coordinates for element '{nom_element}': {e}")

    logger.warning(f"No coordinates found for element '{nom_element}'")
    return None


def get_image_path(image_filename: str) -> str:
    """
    Construct the full path to an image file based on a partial filename without extension.

    Args:
        image_filename: Partial name of the image file without extension

    Returns:
        String path to the image file

    Raises:
        FileNotFoundError: If no matching image file is found
    """
    # Chemin du répertoire des images
    photos_dir = os.path.join(settings.MEDIA_ROOT, "photos")

    # Vérifier si le répertoire existe
    if not os.path.exists(photos_dir):
        logger.error(f"Photos directory not found: {photos_dir}")
        raise FileNotFoundError(f"Photos directory not found: {photos_dir}")

    # Parcourir les fichiers du répertoire pour trouver une correspondance
    for filename in os.listdir(photos_dir):
        # Obtenir le nom du fichier sans extension
        name_without_ext = os.path.splitext(filename)[0]

        # Vérifier si le nom partiel est contenu dans le nom du fichier
        if image_filename in name_without_ext:
            return os.path.join(photos_dir, filename)

    # Si aucun fichier correspondant n'est trouvé
    logger.error(f"No image file found matching: {image_filename}")
    raise FileNotFoundError(f"No image file found matching: {image_filename}")


from collections.abc import Mapping


def calculate_position(
    alignment: str,
    element_width: int,
    element_height: int,
    coords: Mapping[str, Tuple[Union[int, float], Union[int, float]]],
    offset_x: int = 0,
    offset_y: int = 0,
) -> Tuple[int, int]:
    """
    Calculate the position based on alignment and coordinates.

    Args:
        alignment: Alignment type (e.g., 'top_left', 'center')
        element_width: Width of the element to place
        element_height: Height of the element to place
        coords: Dictionary of coordinate points
        offset_x: Horizontal offset
        offset_y: Vertical offset

    Returns:
        (x, y) position tuple
    """
    coin_sup_gauche = coords.get("Coin supérieur gauche")
    centre = coords.get("Centre")

    if not coin_sup_gauche or not centre:
        logger.error(
            f"Missing required coordinate points. Available: {list(coords.keys())}"
        )
        raise ValueError(
            f"Missing required coordinate points. Need 'Coin supérieur gauche' and 'Centre'"
        )

    # Convert to integers to avoid division problems
    x_center = int(centre[0])
    y_center = int(centre[1])
    x_top_left = int(coin_sup_gauche[0])
    y_top_left = int(coin_sup_gauche[1])

    position_map = {
        "top_left": (x_top_left + offset_x, y_top_left + offset_y),
        "top_center": (
            x_center - (element_width // 2) + offset_x,
            y_top_left + offset_y,
        ),
        "center_vertical_left": (
            x_top_left + offset_x,
            y_center - (element_height // 2) + offset_y,
        ),
        "center": (
            x_center - (element_width // 2) + offset_x,
            y_center - (element_height // 2) + offset_y,
        ),
        "left_center": (
            x_top_left + offset_x,
            y_center - (element_height // 2) + offset_y,
        ),
    }

    if alignment in position_map:
        return position_map[alignment]

    logger.warning(f"Unknown alignment: '{alignment}', using 'top_left' instead")
    return position_map["top_left"]


def generate_qr_code(
    value: str,
    scale: int = 5,
    border: int = 1,
    dark: str = "black",
    light: str = "white",
) -> Image.Image:
    """
    Generate a QR code using segno and convert it to a PIL Image.

    Args:
        value: Content to encode in the QR code
        scale: Scale of the QR code
        border: Border width around the QR code
        dark: Color of the QR code modules
        light: Background color

    Returns:
        PIL Image containing the QR code
    """
    try:
        # Create QR code with segno
        qr = segno.make(value)

        # Create a BytesIO object to hold the PNG data
        buffer = io.BytesIO()

        # Save the QR code as PNG to the buffer
        qr.save(buffer, kind="png", scale=scale, border=border, dark=dark, light=light)

        # Reset buffer position to the beginning
        buffer.seek(0)

        # Open the buffer as a PIL Image
        qr_image = Image.open(buffer)

        logger.debug(f"Generated QR code for '{value}' with dimensions {qr_image.size}")

        return qr_image

    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}")
        raise CertificateGenerationError(f"Failed to generate QR code: {e}") from e


def place_image(
    draw: ImageDraw.ImageDraw,
    img: Image.Image,
    nom_element: str,
    coords: Dict[str, Tuple[int, int]],
    contenu: Dict[str, Any],
    align: str = "top_left",
    offset_x: int = 0,
    offset_y: int = 0,
) -> None:
    """
    Place an image on the template image based on coordinates and alignment.

    Args:
        draw: ImageDraw object
        img: Base image to place on
        nom_element: Element name
        coords: Coordinate dictionary
        contenu: Content dictionary with image information
        align: Alignment type
        offset_x: Horizontal offset
        offset_y: Vertical offset

    Raises:
        FileNotFoundError: If the image file doesn't exist
    """
    if "valeur" not in contenu:
        logger.error(
            f"Missing 'valeur' key in content for image element '{nom_element}'"
        )
        raise ValueError(
            f"Missing 'valeur' key in content for image element '{nom_element}'"
        )

    try:
        # Get rectangle dimensions
        coin_sup_gauche = coords["Coin supérieur gauche"]
        coin_inf_droit = coords["Coin inférieur droit"]
        largeur_rect = int(coin_inf_droit[0] - coin_sup_gauche[0])
        hauteur_rect = int(coin_inf_droit[1] - coin_sup_gauche[1])

        # Handle QR codes differently
        if nom_element in ["QR", "QR 2"]:
            # Generate QR code with segno
            scale = int(contenu.get("scale", 5))
            border = int(contenu.get("border", 1))
            dark = contenu.get("dark", "black")
            light = contenu.get("light", "white")

            image_element = generate_qr_code(
                contenu["valeur"], scale, border, dark, light
            )
        else:
            # Handle regular images
            image_path = get_image_path(contenu["valeur"])
            image_element = resize_logo_for_template(image_path,coin_sup_gauche,coin_inf_droit)

        # Resize image to fit the rectangle
        image_element = image_element

        # Calculate position based on alignment
        position = calculate_position(
            align, largeur_rect, hauteur_rect, coords, offset_x, offset_y
        )

        # Ensure position values are integers
        position = (int(position[0]), int(position[1]))

        # Paste image on template
        img.paste(image_element, position)
        logger.debug(
            f"Successfully placed {'QR code' if nom_element in ['QR', 'QR 2'] else 'image'} '{nom_element}' at position {position}"
        )

    except FileNotFoundError as e:
        if nom_element not in ["QR", "QR 2"]:  # Only raise for regular images
            logger.error(
                f"Image file not found: {contenu.get('valeur', 'Unknown')} for element '{nom_element}'"
            )
            raise e
    except Exception as e:
        logger.error(
            f"Error placing {'QR code' if nom_element in ['QR', 'QR 2'] else 'image'} '{nom_element}': {e}"
        )
        raise CertificateGenerationError(
            f"Failed to place {'QR code' if nom_element in ['QR', 'QR 2'] else 'image'} '{nom_element}': {e}"
        ) from e


def load_font(
    font_name: str, size: int
) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
    """
    Load a font by name and size.

    Args:
        font_name: Name of the font file
        size: Font size

    Returns:
        Font object

    Raises:
        IOError: If the font file cannot be loaded
    """
    try:
        font_path = os.path.join(settings.STATIC_ROOT, "fonts", font_name)
        if not os.path.exists(font_path):
            logger.warning(f"Font file not found: {font_path}, using default font")
            return ImageFont.load_default()
        return ImageFont.truetype(font_path, size)
    except IOError as e:
        logger.error(f"Error loading font '{font_name}': {e}")
        return ImageFont.load_default()


def place_text(
    draw: ImageDraw.ImageDraw,
    img: Image.Image,
    nom_element: str,
    coords: Dict[str, Tuple[int, int]],
    contenu: Dict[str, Any],
    align: str = "top_left",
    offset_x: int = 0,
    offset_y: int = 0,
) -> None:
    """
    Place text on the template image based on coordinates and alignment.

    Args:
        draw: ImageDraw object
        img: Base image to place on
        nom_element: Element name
        coords: Coordinate dictionary
        contenu: Content dictionary with text information
        align: Alignment type
        offset_x: Horizontal offset
        offset_y: Vertical offset
    """
    if "valeur" not in contenu:
        logger.error(
            f"Missing 'valeur' key in content for text element '{nom_element}'"
        )
        raise ValueError(
            f"Missing 'valeur' key in content for text element '{nom_element}'"
        )

    try:
        valeur = str(contenu["valeur"])
        taille_police = int(contenu.get("taille_police", 20))
        couleur = contenu.get("couleur", "black")
        font_name = contenu.get("font", "ARIALBD.TTF")

        # Load font
        font = load_font(font_name, taille_police)

        # Measure text size
        bbox = font.getbbox(valeur)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position based on alignment
        position = calculate_position(
            align, int(text_width), int(text_height), coords, offset_x, offset_y
        )

        # Draw text
        draw.text(position, valeur, font=font, fill=couleur)
        logger.debug(
            f"Successfully placed text '{nom_element}' with value '{valeur}' at position {position}"
        )

    except Exception as e:
        logger.error(f"Error placing text '{nom_element}': {e}")
        raise CertificateGenerationError(
            f"Failed to place text '{nom_element}': {e}"
        ) from e


def generate_habilitation_certificate(
    data: Dict[str, Dict[str, Any]],
    coordonnees_rectangles: Dict[str, Dict[str, Tuple[int, int]]],
    output_path: str,
) -> bool:
    """
    Generate a certificate based on provided data and coordinates.

    Args:
        data: Dictionary of elements to place on the certificate
        coordonnees_rectangles: Dictionary of coordinate data
        output_path: Path where the output image will be saved

    Returns:
        True if successful, False otherwise

    Raises:
        CertificateGenerationError: If the certificate generation fails
    """
    logger.info(f"Generating certificate to {output_path}")

    try:
        # Open template image
        template_path = os.path.join(settings.STATIC_ROOT, "images", "he13.png")
        if not os.path.exists(template_path):
            logger.error(f"Template image not found: {template_path}")
            raise FileNotFoundError(f"Template image not found: {template_path}")

        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)

        # Set counters for logging
        total_elements = len(data)
        processed_elements = 0
        failed_elements = 0

        # Séparer les éléments en deux catégories : images et textes
        image_elements = {}
        text_elements = {}

        for nom_element, contenu in data.items():
            if nom_element in ["Logo", "Photo", "QR", "QR 2"]:
                image_elements[nom_element] = contenu
            else:
                text_elements[nom_element] = contenu

        # Traiter d'abord les images
        logger.info("Processing image elements first")
        for nom_element, contenu in image_elements.items():
            try:
                # Find coordinates for the element
                coords = get_coordinates_for_element(
                    nom_element, coordonnees_rectangles
                )

                if not coords:
                    logger.warning(
                        f"No coordinates found for element '{nom_element}', skipping"
                    )
                    failed_elements += 1
                    continue

                # Extract placement options
                align = contenu.get("align", "top_left")
                offset_x = int(contenu.get("offset_x", 0))
                offset_y = int(contenu.get("offset_y", 0))

                logger.debug(f"Placing image element: {nom_element}")
                place_image(
                    draw,
                    img,
                    nom_element,
                    coords,
                    contenu,
                    align,
                    offset_x,
                    offset_y,
                )
                processed_elements += 1

            except Exception as e:
                logger.error(f"Failed to process image element '{nom_element}': {e}")
                failed_elements += 1

        # Puis traiter les textes
        logger.info("Processing text elements")
        for nom_element, contenu in text_elements.items():
            try:
                # Find coordinates for the element
                coords = get_coordinates_for_element(
                    nom_element, coordonnees_rectangles
                )

                if not coords:
                    logger.warning(
                        f"No coordinates found for element '{nom_element}', skipping"
                    )
                    failed_elements += 1
                    continue

                # Extract placement options
                align = contenu.get("align", "top_left")
                offset_x = int(contenu.get("offset_x", 0))
                offset_y = int(contenu.get("offset_y", 0))

                logger.debug(f"Placing text element: {nom_element}")
                place_text(
                    draw,
                    img,
                    nom_element,
                    coords,
                    contenu,
                    align,
                    offset_x,
                    offset_y,
                )
                processed_elements += 1

            except Exception as e:
                logger.error(f"Failed to process text element '{nom_element}': {e}")
                failed_elements += 1

        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the generated image
        img.save(output_path)

        logger.info(
            f"Certificate generation completed. Processed {processed_elements}/{total_elements} elements. Failed: {failed_elements}"
        )
        return processed_elements > 0 and failed_elements == 0

    except Exception as e:
        logger.error(f"Certificate generation failed: {e}")
        raise CertificateGenerationError(f"Certificate generation failed: {e}") from e
