import io
import os
import tempfile
import zipfile
import logging
import shutil
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from PIL import Image
from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from .generate_certificate import generate_habilitation_certificate, CertificateGenerationError
from .data import load_data_from_excel

# Configure logging
logger = logging.getLogger(__name__)

class HabilitationFileSerializer(serializers.Serializer):
    """Serializer for validating uploaded Excel files."""
    excel_file = serializers.FileField(required=True)

class HabilitationError(Exception):
    """Custom exception for habilitation process errors."""
    pass

class HabilitationGenerateView(APIView):
    """
    API view for generating habilitation certificates from an Excel file.
    
    This view accepts an Excel file upload, processes the data to generate 
    certificates, and returns a zip file containing:
    - PNG images of the front and back of each certificate
    - PDF files combining the front and back for each person
    """
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        """
        Process the uploaded Excel file and generate certificates.
        
        Args:
            request: HTTP request object with multipart form data
            
        Returns:
            HTTP response with a zip file containing certificates
        """
        logger.info("Processing habilitation certificate generation request")
        temp_dir = None
        
        try:
            # Validate the uploaded file
            excel_file = self._validate_request(request)
            
            # Load and process the Excel data
            all_data = self._load_excel_data(excel_file)
            
            # Load coordinate data for certificate elements
            coordonnees_rectangles = self._load_coordinates()
            
            # Create temporary directory for files
            temp_dir = tempfile.mkdtemp()
            logger.debug(f"Created temporary directory: {temp_dir}")
            
            # Generate zip file with certificates
            zip_buffer = self._generate_certificates(all_data, coordonnees_rectangles, temp_dir)
            
            # Return the zip file as response
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type="application/zip")
            response['Content-Disposition'] = 'attachment; filename=habilitations.zip'
            logger.info("Certificate generation completed successfully")
            return response
            
        except HabilitationError as e:
            logger.error(f"Habilitation generation error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during certificate generation: {e}")
            return Response(
                {"error": f"Erreur inattendue lors de la génération des certificats : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # Clean up temporary files
            self._cleanup_temp_files(temp_dir)
    
    def _validate_request(self, request) -> Any:
        """
        Validate the request and extract the Excel file.
        
        Args:
            request: HTTP request object
            
        Returns:
            Validated Excel file
            
        Raises:
            HabilitationError: If validation fails
        """
        serializer = HabilitationFileSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Request validation failed: {serializer.errors}")
            raise HabilitationError(f"Validation des données échouée: {serializer.errors}")
        
        try:
            if not hasattr(serializer, 'validated_data') or not isinstance(serializer.validated_data, dict) or 'excel_file' not in serializer.validated_data:
                raise HabilitationError("Données de fichier Excel manquantes")
            excel_file = serializer.validated_data['excel_file']
            if not excel_file:
                raise HabilitationError("Aucun fichier n'a été fourni")
            return excel_file
        except Exception as e:
            logger.error(f"Error extracting file from request: {e}")
            raise HabilitationError(f"Erreur lors de l'extraction du fichier : {str(e)}")
    
    def _load_excel_data(self, excel_file) -> List[Dict[str, Any]]:
        """
        Load and process the Excel file data.
        
        Args:
            excel_file: Uploaded Excel file
            
        Returns:
            List of dictionaries containing certificate data
            
        Raises:
            HabilitationError: If Excel processing fails
        """
        try:
            logger.debug("Loading data from Excel file")
            all_data = load_data_from_excel(excel_file)
            logger.info(f"Successfully loaded data for {len(all_data)} certificates")
            return all_data
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            raise HabilitationError(f"Erreur lors du traitement du fichier Excel : {str(e)}")
    
    def _load_coordinates(self) -> Dict[str, Dict[str, Tuple[int, int]]]:
        """
        Load the coordinates data from the JSON file.
        
        Returns:
            Dictionary of coordinate data
            
        Raises:
            HabilitationError: If coordinate file is missing or invalid
        """
        import json
        
        coordonnees_path = os.path.join(settings.BASE_DIR, 'static', 'json', 'coordonnees_HE.json')
        try:
            logger.debug(f"Loading coordinates from {coordonnees_path}")
            with open(coordonnees_path, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logger.error(f"Coordinates file not found: {coordonnees_path}")
            raise HabilitationError("Le fichier coordonnees_HE.json est introuvable.")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in coordinates file: {e}")
            raise HabilitationError(f"Format de fichier de coordonnées invalide : {str(e)}")
    
    def _generate_certificates(
        self, 
        all_data: List[Dict[str, Any]], 
        coordonnees_rectangles: Dict[str, Dict[str, Tuple[int, int]]],
        temp_dir: str
    ) -> io.BytesIO:
        """
        Generate certificate images and PDFs, and package them in a zip file.
        
        Args:
            all_data: List of dictionaries containing certificate data
            coordonnees_rectangles: Dictionary of coordinate data
            temp_dir: Temporary directory path
            
        Returns:
            BytesIO buffer containing the zip file
            
        Raises:
            HabilitationError: If generation fails
        """
        zip_buffer = io.BytesIO()
        processed_count = 0
        failed_count = 0
        
        try:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Create directories in zip
                zipf.writestr('pdf/', '')
                zipf.writestr('images/', '')
                
                for i, data in enumerate(all_data):
                    try:
                        person_info = self._get_person_info(data, i)
                        file_paths = self._generate_certificate_files(
                            data, 
                            coordonnees_rectangles, 
                            temp_dir, 
                            person_info
                        )
                        
                        # Add files to zip
                        for src_path, zip_path in file_paths.items():
                            if os.path.exists(src_path):
                                zipf.write(src_path, zip_path)
                            else:
                                logger.warning(f"File not found for adding to zip: {src_path}")
                        
                        processed_count += 1
                        logger.debug(f"Processed certificate {i+1}/{len(all_data)}: {person_info['full_name']}")
                        
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Error processing certificate {i+1}: {e}")
                        continue
                
        except Exception as e:
            logger.error(f"Error creating zip file: {e}")
            raise HabilitationError(f"Erreur lors de la création du fichier zip : {str(e)}")
        
        logger.info(f"Certificate generation summary: {processed_count} successful, {failed_count} failed")
        if processed_count == 0:
            raise HabilitationError("Aucun certificat n'a pu être généré")
        
        return zip_buffer
    
    def _get_person_info(self, data: Dict[str, Any], index: int) -> Dict[str, str]:
        """
        Extract and sanitize person information from certificate data.
        
        Args:
            data: Certificate data dictionary
            index: Index for fallback naming
            
        Returns:
            Dictionary with person information
        """
        nom = data.get("Nom", {}).get("valeur", f"personne_{index + 1}")
        prenom = data.get("Prénom", {}).get("valeur", "")
        full_name = f"{nom}_{prenom}"
        
        # Sanitize filename - replace spaces and multiple underscores
        sanitized_name = full_name.replace(" ", "_").replace("__", "_")
        
        return {
            "nom": nom,
            "prenom": prenom,
            "full_name": full_name,
            "sanitized_name": sanitized_name
        }
    
    def _generate_certificate_files(
        self, 
        data: Dict[str, Any],
        coordonnees_rectangles: Dict[str, Dict[str, Tuple[int, int]]],
        temp_dir: str,
        person_info: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Generate certificate image and PDF files for a single person.
        
        Args:
            data: Certificate data dictionary
            coordonnees_rectangles: Dictionary of coordinate data
            temp_dir: Temporary directory path
            person_info: Dictionary with person information
            
        Returns:
            Dictionary mapping source file paths to zip file paths
            
        Raises:
            HabilitationError: If file generation fails
        """
        sanitized_name = person_info["sanitized_name"]
        
        # Define file paths
        recto_path = os.path.join(temp_dir, f"habilitation_{sanitized_name}_recto.jpeg")
        verso_path = os.path.join(temp_dir, f"habilitation_{sanitized_name}_verso.jpeg")
        pdf_path = os.path.join(temp_dir, f"attestation_{sanitized_name}.pdf")
        
        # Generate front image
        try:
            logger.debug(f"Generating certificate front: {recto_path}")
            success = generate_habilitation_certificate(data, coordonnees_rectangles, recto_path)
            if not success:
                logger.warning(f"Certificate front generation reported issues for {sanitized_name}")
        except CertificateGenerationError as e:
            logger.error(f"Failed to generate certificate front: {e}")
            raise HabilitationError(f"Échec de génération du recto pour {sanitized_name}: {str(e)}")
        
        # Copy back image template
        try:
            logger.debug(f"Generating certificate back: {verso_path}")
            verso_template = Path(settings.STATIC_ROOT) / 'images' / 'he_verso.png'
            if not verso_template.exists():
                logger.warning(f"Back template not found: {verso_template}")
                # Create a blank image as fallback
                blank_img = Image.new('RGB', (800, 500), color='white')
                blank_img.save(verso_path)
            else:
                shutil.copy(verso_template, verso_path)
        except Exception as e:
            logger.error(f"Failed to generate certificate back: {e}")
            raise HabilitationError(f"Échec de génération du verso pour {sanitized_name}: {str(e)}")
        
        # Create PDF with front and back
        try:
            logger.debug(f"Creating PDF: {pdf_path}")
            self._create_pdf(recto_path, verso_path, pdf_path)
        except Exception as e:
            logger.error(f"Failed to create PDF: {e}")
            raise HabilitationError(f"Échec de création du PDF pour {sanitized_name}: {str(e)}")
        
        # Return paths mapping
        return {
            recto_path: f"images/habilitation_{sanitized_name}_recto.jpeg",
            verso_path: f"images/habilitation_{sanitized_name}_verso.jpeg",
            pdf_path: f"pdf/attestation_{sanitized_name}.pdf"
        }
    
    def _create_pdf(self, recto_path: str, verso_path: str, pdf_path: str) -> None:
        """
        Create a PDF with front and back certificate images.
        
        Args:
            recto_path: Path to front image
            verso_path: Path to back image
            pdf_path: Path to save PDF
            
        Raises:
            Exception: If PDF creation fails
        """
        pdf_buffer = io.BytesIO()
        
        try:
            with Image.open(recto_path) as img_recto, Image.open(verso_path) as img_verso:
                width, height = img_recto.size
                
                c = canvas.Canvas(pdf_buffer, pagesize=(width, height))
                c.drawImage(ImageReader(img_recto), 0, 0, width=width, height=height)
                c.showPage()
                c.drawImage(ImageReader(img_verso), 0, 0, width=width, height=height)
                c.showPage()
                c.save()
                
            # Write PDF to file
            with open(pdf_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
                
        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            raise Exception(f"Erreur lors de la création du PDF: {str(e)}")
    
    def _cleanup_temp_files(self, temp_dir: Optional[str]) -> None:
        """
        Clean up temporary files and directory.
        
        Args:
            temp_dir: Temporary directory to clean up
        """
        if temp_dir and os.path.exists(temp_dir):
            try:
                logger.debug(f"Cleaning up temporary directory: {temp_dir}")
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Error cleaning up temporary directory: {e}")