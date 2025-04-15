import os
from pathlib import Path
from typing import Dict, Tuple, Union, Optional
from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
import ast
import segno
import uuid

# --- Data Classes and Custom Exceptions ---

@dataclass
class Coordinates:
    """Represents coordinates for element placement."""
    top_left: Tuple[int, int]
    bottom_right: Tuple[int, int]
    center: Tuple[int, int]

    @property
    def width(self) -> int:
        return self.bottom_right[0] - self.top_left[0]
    
    @property
    def height(self) -> int:
        return self.bottom_right[1] - self.top_left[1]

class DocumentGenerationError(Exception):
    """Custom exception for document generation errors."""
    pass

# --- Coordinate Management ---

def get_coordinates_for_element(nom_element: str, coordonnees_rectangles: Dict) -> Optional[Dict]:
    """Returns coordinates associated with a given element."""
    try:
        for encoded_key, coords in coordonnees_rectangles.items():
            key_list = ast.literal_eval(encoded_key)
            if key_list[0] == nom_element:
                return coords
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing coordinates for '{nom_element}': {e}")
    return None

def calculate_position(
    coords: Dict,
    dimensions: Tuple[int, int],
    alignment: str,
    offset_x: int,
    offset_y: int
) -> Tuple[int, int]:
    """Calculate position for element placement."""
    width, height = dimensions
    top_left = coords["Coin supérieur gauche"]
    center = coords["Centre"]
    
    positions = {
        "top_left": (
            top_left[0] + offset_x,
            top_left[1] + offset_y
        ),
        "center": (
            center[0] - (width // 2) + offset_x,
            center[1] - (height // 2) + offset_y
        ),
        "left_center": (
            top_left[0] + offset_x,
            center[1] - (height // 2) + offset_y
        ),
        "center_vertical_left": (
            top_left[0] + offset_x,
            center[1] - (height // 2) + offset_y
        )
    }
    
    return positions.get(alignment, positions["top_left"])

# --- Image Processing ---

def generate_qr_code(url: str, scale: int = 10) -> Image.Image:
    """Generate a QR code image."""
    qr = segno.make(url)
    qr_io = BytesIO()
    qr.save(qr_io, kind='png', scale=scale, border=0)
    qr_io.seek(0)
    return Image.open(qr_io)

def load_image(image_source: Union[str, Image.Image, None], photos_dir: Optional[Path] = None) -> Image.Image:
    """Load an image from various sources."""
    try:
        if isinstance(image_source, str):
            if photos_dir:
                image_path = photos_dir / image_source
                if not image_path.exists():
                    raise FileNotFoundError(f"Image not found: {image_path}")
                return Image.open(image_path)
            return Image.open(image_source)
        elif isinstance(image_source, Image.Image):
            return image_source
        else:
            raise ValueError("Invalid image source type")
    except Exception as e:
        raise DocumentGenerationError(f"Failed to load image: {str(e)}")

def resize_image(image: Image.Image, width: int, height: int, maintain_aspect_ratio: bool = False) -> Image.Image:
    """Resize image according to specifications."""
    if maintain_aspect_ratio:
        image.thumbnail((width, height), Image.LANCZOS)
        return image
    return image.resize((width, height), Image.LANCZOS)

# --- Element Placement ---

def place_image(
    img: Image.Image,
    image_to_place: Union[str, Image.Image, None],
    element_name: str,
    coords: Dict,
    content: Dict,
    alignment: str = "top_left",
    offset_x: int = 0,
    offset_y: int = 0
) -> None:
    """Place an image on the template."""
    try:
        # Handle QR code generation
        if element_name.startswith('QR'):
            unique_id = str(uuid.uuid4())
            url = f"https://kesdocs.vercel.app/verify/{unique_id}"
            image = generate_qr_code(url)
        else:
            image = load_image(image_to_place)

        # Get dimensions and resize
        width = coords["Coin inférieur droit"][0] - coords["Coin supérieur gauche"][0]
        height = coords["Coin inférieur droit"][1] - coords["Coin supérieur gauche"][1]
        image = resize_image(image, width, height, content.get("maintain_aspect_ratio", False))

        # Calculate position and paste
        position = calculate_position(
            coords,
            image.size,
            alignment,
            offset_x,
            offset_y
        )
        img.paste(image, position)

    except Exception as e:
        raise DocumentGenerationError(f"Error placing image for '{element_name}': {str(e)}")

def place_photo(
    img: Image.Image,
    element_name: str,
    coords: Dict,
    content: Dict,
    alignment: str = "top_left",
    offset_x: int = 0,
    offset_y: int = 0
) -> None:
    """Place a photo on the template."""
    try:
        photos_dir = Path(staticfiles_storage.path('images/photos/imgsd'))
        valeur = str(content.get("valeur", ""))
        print(f"Loading photo: {valeur}")
        
        # Skip if value is nan or empty
        if valeur.lower() == "nan" or not valeur:
            print(f"Skipping photo placement for {element_name}: empty or nan value")
            return
            
        # Handle spaces in filename
        valeur = valeur.strip()
        
        image = load_image(valeur, photos_dir)
        width = coords["Coin inférieur droit"][0] - coords["Coin supérieur gauche"][0]
        height = coords["Coin inférieur droit"][1] - coords["Coin supérieur gauche"][1]
        
        resized_image = resize_image(
            image,
            width,
            height,
            maintain_aspect_ratio=content.get("maintain_aspect_ratio", False)
        )
        
        position = calculate_position(
            coords,
            resized_image.size,
            alignment,
            offset_x,
            offset_y
        )
        
        img.paste(resized_image, position)
        
    except Exception as e:
        raise DocumentGenerationError(f"Error placing photo for '{element_name}': {str(e)}")

def place_text(
    draw: ImageDraw.ImageDraw,
    nom_element: str,
    coords: Dict,
    contenu: Dict,
    alignment: str = "top_left",
    offset_x: int = 0,
    offset_y: int = 0
) -> None:
    """Place text on the image."""
    try:
        # Handle text value
        valeur = str(contenu.get("valeur", ""))
        if valeur.lower() == "nan":
            valeur = ""

        # Get font settings
        taille_police = contenu.get("taille_police", 20)
        couleur = contenu.get("couleur", "black")

        # Load font
        try:
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')
            font = ImageFont.truetype(font_path, taille_police)
        except IOError:
            print(f"Warning: Using default font for '{nom_element}' - ARIALBD.TTF not found")
            font = ImageFont.load_default()

        # Get text dimensions and calculate position
        bbox = font.getbbox(valeur)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = calculate_position(
            coords,
            (int(text_width), int(text_height)),
            alignment,
            offset_x,
            offset_y
        )

        # Draw text
        draw.text(position, valeur, font=font, fill=couleur)

    except Exception as e:
        print(f"Warning: Error placing text for '{nom_element}': {str(e)}")

# --- Main Certificate Generation ---

def generate_habilitation_certificate(
    data: Dict,
    coordonnees_rectangles: Dict,
    output_path: str
) -> None:
    """Generate a certification document."""
    try:
        # Open template image
        template_path = os.path.join(settings.STATIC_ROOT, 'images', 'he2.png')
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)

        # Process elements in specific order: first images, then text
        
        # First pass: Process all images (QR codes and photos)
        for nom_element, contenu in data.items():
            if not (nom_element.startswith('QR') or nom_element.startswith('Photo') or nom_element.startswith('Logo')):
                continue
                
            coords = get_coordinates_for_element(nom_element, coordonnees_rectangles)
            if not coords:
                print(f"Warning: No coordinates found for '{nom_element}'")
                continue

            align = contenu.get("align", "top_left")
            offset_x = contenu.get("offset_x", 0)
            offset_y = contenu.get("offset_y", 0)

            if nom_element.startswith('QR'):
                place_image(img, None, nom_element, coords, contenu, align, offset_x, offset_y)
            elif nom_element.startswith('Photo'):
                place_photo(img, nom_element, coords, contenu, align, offset_x, offset_y)
            elif nom_element.startswith('Logo'):
                place_photo(img, nom_element, coords, contenu, align, offset_x, offset_y)
        
        # Second pass: Process all text elements
        for nom_element, contenu in data.items():
            if (nom_element.startswith('QR') or nom_element.startswith('Photo') or nom_element.startswith('Logo')):
                continue
                
            coords = get_coordinates_for_element(nom_element, coordonnees_rectangles)
            if not coords:
                print(f"Warning: No coordinates found for '{nom_element}'")
                continue

            align = contenu.get("align", "top_left")
            offset_x = contenu.get("offset_x", 0)
            offset_y = contenu.get("offset_y", 0)

            place_text(draw, nom_element, coords, contenu, align, offset_x, offset_y)

        # Save the generated document
        img.save(output_path)

    except Exception as e:
        raise DocumentGenerationError(f"Error generating certificate: {str(e)}")