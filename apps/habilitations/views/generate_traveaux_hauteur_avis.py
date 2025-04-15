import os
import re
import uuid
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import zipfile
import pandas as pd
import json
import segno
import logging

logger = logging.getLogger(__name__)

@dataclass
class TextStyle:
    """Configuration for text rendering."""
    font_size: int = 20
    color: str = "black"
    alignment: str = "center"
    anchor: str = "mm"

class DocumentGenerator:
    """Handles document generation logic."""
    
    def __init__(self, font_path: str):
        self.font_path = font_path
        self.fonts_cache = {}

    def get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get cached font instance."""
        if size not in self.fonts_cache:
            self.fonts_cache[size] = ImageFont.truetype(self.font_path, size)
        return self.fonts_cache[size]

    @staticmethod
    def generate_qr_code(url: str, size: Tuple[int, int]) -> Image.Image:
        """Generate QR code with specified dimensions."""
        qr = segno.make(url)
        qr_io = BytesIO()
        qr.save(qr_io, kind='png', scale=10, border=0)
        qr_io.seek(0)
        qr_image = Image.open(qr_io)
        return qr_image.resize(size)

    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitize name for file naming."""
        name = re.sub(r'[\d\s]', '_', name)
        return re.sub(r'__+', '_', name)

    def calculate_text_position(self, coord: Dict, style: TextStyle) -> Tuple[int, int]:
        """Calculate text position based on alignment."""
        if style.alignment == "star":
            top_left = coord.get("Coin supérieur gauche", [0, 0])
            bottom_left = coord.get("Coin inférieur gauche", [0, 0])
            return (top_left[0] + 3, ((top_left[1] + bottom_left[1]) // 2) - 3)
        elif style.alignment == "center":
            return coord.get("Centre", [0, 0])
        return coord.get("Coin supérieur gauche", [0, 0])

    def determine_text_style(self, color_key: str, value: str) -> TextStyle:
        """Determine text styling based on color key and value."""
        style = TextStyle()
        
        if "violet" in color_key or "rose" in color_key:
            style.alignment = "center"
            if "10" in color_key:
                style.font_size = 22
            elif value.lower() == "apte":
                style.color = "green"
            elif value.lower() == "inapte":
                style.color = "red"
            elif value.lower() == "sans objet":
                style.color = "orange"
        elif "jaune" in color_key:
            style.font_size = 22 if "10" in color_key else 20
            style.alignment = "center" if "10" in color_key else "center"
            
        return style

class HabilitationTitleGenerator:
    """Main class for generating habilitation titles."""
    
    def __init__(self, base_image_path: str, photos_folder: str, coordinates_path: str, font_path: str):
        self.base_image_path = base_image_path
        self.photos_folder = photos_folder
        self.coordinates = self.load_coordinates(coordinates_path)
        self.document_generator = DocumentGenerator(font_path)
        
    @staticmethod
    def load_coordinates(path: str) -> Dict:
        """Load and validate coordinates configuration."""
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Invalid coordinates file: {str(e)}")

    def find_photo(self, name: str) -> Optional[str]:
        """
        Find participant's photo in the photos directory.

        Args:
            name: The participant's name to search for

        Returns:
            Optional[str]: Full path to the photo if found, None otherwise
        """
        name_parts = name.lower().split()

        for file in os.listdir(self.photos_folder):
            file_lower = file.lower()
            if not (file_lower.endswith('.jpg') or file_lower.endswith('.jpeg')):
                continue

            # Check if all parts of the name appear in the filename
            if all(part in file_lower for part in name_parts):
                return os.path.join(self.photos_folder, file)

        return None

    def get_field_value(self, row: pd.Series, field_name: str, habilitation_number: str) -> str:
        """Get field value with special handling for certain fields."""
        if field_name == "N° de l'habilitation":
            return habilitation_number
        elif field_name == "N° du rapport":
            return row.get('N° du rapport d’équipe', '')
        elif field_name == "Date de la formation":
            date_start = row.get('Date de la formation')
            date_end = row.get('Fin de la formation')
            if pd.notna(date_start) and pd.notna(date_end):
                from apps.habilitations.utils import format_date_range
                return format_date_range(date_start, date_end)
            return ""
        elif field_name == "Titulaire":
            nom = str(row.get('Nom', ''))
            prenom = str(row.get('Prénom', ''))
            if pd.isna(prenom):
                prenom = ""
            full_name = f"{nom}_{prenom}".replace('_', ' ').strip()
            return re.sub(r'\s+', ' ', full_name)
        
        # Get regular field value
        value = row.get(field_name, "")
        
        # Handle non-string and NaN values
        if pd.isna(value):
            return ""
        if not isinstance(value, str):
            return str(value)
            
        return value

    def generate_title(self, row: pd.Series, habilitation_number: str) -> Tuple[BytesIO, BytesIO]:
        """Generate both PNG and PDF versions of the habilitation title."""
        # Load base image
        image = Image.open(self.base_image_path).convert('RGB')
        draw = ImageDraw.Draw(image)

        # Generate verification URL and QR code
        unique_id = str(uuid.uuid4())
        url = f"https://kesdocs.vercel.app/verify/{unique_id}"

        # Process each field from coordinates
        for field_key, coord in self.coordinates.items():
            try:
                field_info = eval(field_key)  # Safely evaluate field configuration
                field_name, color_key = field_info

                # Get field value
                value = self.get_field_value(row, field_name, habilitation_number)

                # Handle special fields
                if "qrc" in field_name:
                    top_left = coord.get("Coin supérieur gauche", [0, 0])
                    bottom_right = coord.get("Coin inférieur droit", [0, 0])
                    qr_width = bottom_right[0] - top_left[0]
                    qr_height = bottom_right[1] - top_left[1]
                    qr_image = self.document_generator.generate_qr_code(url, (qr_width, qr_height))
                    image.paste(qr_image, tuple(coord["Coin supérieur gauche"]))
                    continue

                if "photo" in field_name:
                    photo_path = self.find_photo(row['Photo'])
                    print(photo_path)
                    if photo_path:
                        try:
                            with Image.open(photo_path) as photo:
                                top_left = coord.get("Coin supérieur gauche", [0, 0])
                                bottom_right = coord.get("Coin inférieur droit", [0, 0])
                                width = bottom_right[0] - top_left[0]
                                height = bottom_right[1] - top_left[1]
                                photo_resized = photo.resize((width, height))
                                image.paste(photo_resized, tuple(top_left))
                        except Exception as e:
                            logger.error(f"Error adding photo {photo_path}: {str(e)}")
                    continue

                # Add text with styling
                style = self.document_generator.determine_text_style(color_key, value)
                position = self.document_generator.calculate_text_position(coord, style)
                font = self.document_generator.get_font(style.font_size)
                draw.text(position, str(value), fill=style.color, font=font, anchor=style.anchor)

            except Exception as e:
                logger.error(f"Error processing field {field_key}: {str(e)}")
                continue

        # Generate PNG and PDF versions
        png_io = BytesIO()
        image.save(png_io, format="PNG")
        png_io.seek(0)

        pdf_io = BytesIO()
        pdf = canvas.Canvas(pdf_io)
        pdf.drawImage(ImageReader(png_io), 0, 0, width=595, height=842)
        pdf.save()
        pdf_io.seek(0)

        return png_io, pdf_io

class GenerateHabilitationTitlesTHView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            # Initialize paths
            image_file = staticfiles_storage.path('images/th6.png')
            images_folder = staticfiles_storage.path('images/photos/imgsd')
            json_path = staticfiles_storage.path('json/coordonne_TH.json')
            font_path = staticfiles_storage.path('fonts/ARIALBD.TTF')

            # Validate input file
            excel_file = request.FILES.get('file')
            if not excel_file:
                return Response(
                    {"error": "Excel file is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Initialize generator
            generator = HabilitationTitleGenerator(
                image_file, images_folder, json_path, font_path
            )

            # Read Excel data
            df = pd.read_excel(excel_file)

            # Prepare ZIP file
            zip_io = BytesIO()
            with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for index, row in df.iterrows():
                    try:
                        habilitation_number = row.get('N° de l’habilitation', '')
                        png_io, pdf_io = generator.generate_title(row, habilitation_number)

                        # Add files to ZIP
                        participant_name = generator.document_generator.sanitize_name(
                            f"{row.get('Nom', '')}_{row.get('Prénom', '')}"
                        )

                        zip_file.writestr(
                            f"images/{participant_name}_habilitation.png",
                            png_io.getvalue()
                        )
                        zip_file.writestr(
                            f"pdf/{participant_name}_habilitation.pdf",
                            pdf_io.getvalue()
                        )

                    except Exception as e:
                        logger.error(f"Error processing row {index}: {str(e)}")
                        continue

            # Prepare response
            zip_io.seek(0)
            response = HttpResponse(zip_io, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="habilitations.zip"'
            return response

        except Exception as e:
            logger.error(f"Error generating habilitation titles: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            # Cleanup
            if 'excel_file' in locals():
                excel_file.close()
            if 'zip_io' in locals():
                zip_io.close()