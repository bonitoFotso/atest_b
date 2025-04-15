# apps/inspections/views.py
import os
import uuid
import zipfile
from io import BytesIO
from pathlib import Path
import logging

import segno
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Max
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.models import QRCode
from apps.inspections.models import Etiquette
from apps.inspections.serializers import EtiquetteAutoCreateSerializer
from apps.utils import get_font_for_text, draw_centered_text

# Configurer le logger
logger = logging.getLogger(__name__)


class GenerateEtiquettesView(APIView):
    """
    Vue pour générer automatiquement des étiquettes pour un site et un type d'inspection donnés,
    ainsi que des fichiers d'étiquettes en fonction du type d'inspection.
    """

    def post(self, request, *args, **kwargs):
        """
        Endpoint POST pour générer des étiquettes et retourner un fichier ZIP.
        """
        serializer = EtiquetteAutoCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Récupérer les données validées
            client = serializer.validated_data['client']
            site = serializer.validated_data['site']
            inspection_type = serializer.validated_data['inspectionType']
            nombre = serializer.validated_data['nombre']

            # Trouver le dernier numéro déjà utilisé
            dernier_numero = Etiquette.objects.filter(
                client=client, 
                site=site, 
                inspectionType=inspection_type
            ).aggregate(max_numero=Max('numero'))['max_numero'] or 0

            # Commencer à partir du dernier numéro + 1
            numero_debut = dernier_numero + 1
            logger.info(f"Génération de {nombre} étiquettes pour {client.name}/{site.name}/{inspection_type.name} "
                        f"à partir du numéro {numero_debut}")

            # Générer les étiquettes et le fichier ZIP
            zip_buffer, etiquettes = self._generate_etiquettes_and_zip(
                client, site, inspection_type, numero_debut, nombre
            )

            # Créer la réponse HTTP avec le fichier ZIP
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = (
                f'attachment; filename="etiquettes_{site.name}_{inspection_type.name}.zip"'
            )

            return response

        except Exception as e:
            logger.error(f"Erreur lors de la génération des étiquettes: {str(e)}", exc_info=True)
            return Response(
                {"detail": f"Erreur lors de la génération des étiquettes: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _generate_etiquettes_and_zip(self, client, site, inspection_type, numero_debut, nombre):
        """
        Méthode privée pour générer les étiquettes et le fichier ZIP.
        
        Returns:
            tuple: (BytesIO, list) - Le buffer contenant le ZIP et la liste des étiquettes créées
        """
        etiquettes = []
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for i in range(numero_debut, numero_debut + nombre):
                try:
                    # Générer un QRCode pour l'étiquette
                    qr_code = self._generate_qr_code(i, client, site, inspection_type)
                    
                    # Générer l'image de l'étiquette
                    etiquette_image = self._generate_etiquette_image(
                        inspection_type.name, i, client, site, qr_code
                    )
                    
                    if not etiquette_image:
                        logger.warning(f"L'image de l'étiquette n'a pas pu être générée pour le numéro {i}")
                        continue
                    
                    # Créer l'étiquette dans la base de données
                    etiquette = Etiquette.objects.create(
                        site=site,
                        client=client,
                        inspectionType=inspection_type,
                        numero=i,
                        qrcode=qr_code,
                        image=etiquette_image,
                        isAssigned=False
                    )
                    etiquettes.append(etiquette)
                    
                    # Ajouter l'étiquette au fichier ZIP
                    filename = f"etiquette_{inspection_type.name}_{client.name}_{site.name}_{i}{self._get_extension(etiquette.image.name)}"
                    zip_file.writestr(filename, etiquette.image.read())
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la génération de l'étiquette {i}: {str(e)}")
        
        zip_buffer.seek(0)
        return zip_buffer, etiquettes

    def _get_extension(self, filename):
        """Extraire l'extension d'un nom de fichier"""
        return Path(filename).suffix

    def _generate_qr_code(self, numero, client, site, inspection_type):
        """
        Génère un QR code et le sauvegarde dans la base de données.
        
        Returns:
            QRCode: L'objet QRCode créé
        """
        # Générer un UUID unique pour le QR code
        qr_uuid = uuid.uuid4()
        qr_url = f"{settings.BASE_URL}/rapport/{qr_uuid}/"
        
        # Créer le QR code avec segno
        qr = segno.make(qr_url)
        qr_bytes = BytesIO()
        qr.save(qr_bytes, kind='png', scale=10, border=0)
        qr_bytes.seek(0)
        
        # Définir le chemin de stockage
        qr_path = os.path.join(
            f"{client.name}/{site.name}/{inspection_type.name}", 
            f"qr_code_{numero}.png"
        )
        
        # Créer l'objet QRCode dans la base de données
        qr_code = QRCode.objects.create(
            code=qr_uuid,
            url=qr_url,
            image=ContentFile(qr_bytes.getvalue(), qr_path),
            numero=f"{client.name}_{site.name}_{numero}"
        )
        
        return qr_code

    def _generate_etiquette_image(self, inspection_type_name, numero, client, site, qrcode):
        """
        Génère l'image d'une étiquette en fonction du type d'inspection.
        
        Returns:
            ContentFile or None: Le fichier d'image généré ou None en cas d'erreur
        """
        inspection_type_name = inspection_type_name.lower()
        
        # Mapper les types d'inspection à leurs méthodes de génération
        generators = {
            'levage': self._generate_levage_etiquette,
            'thermographique': self._generate_thermographique_etiquette,
            'extincteur': self._generate_extincteur_etiquette,
            'electrique': self._generate_electrique_etiquette,
        }
        
        if inspection_type_name not in generators:
            logger.error(f"Type d'inspection non pris en charge: {inspection_type_name}")
            raise ValueError(f"Type d'inspection '{inspection_type_name}' non pris en charge.")
            
        return generators[inspection_type_name](numero, client, site, qrcode)

    def _generate_levage_etiquette(self, numero, client, site, qrcode):
        """
        Génère une étiquette pour l'inspection de levage.
        """
        try:
            # Charger l'image de base
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'levage.tif')
            if not os.path.exists(base_image_path):
                logger.error(f"Image de base introuvable: {base_image_path}")
                return None
                
            et_image = Image.open(base_image_path)
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')
            
            # Vérifier si le fichier de police existe
            if not os.path.exists(font_path):
                logger.warning(f"Police introuvable: {font_path}. Utilisation de la police par défaut.")
                font = ImageFont.load_default()
            else:
                font = ImageFont.truetype(font_path, 26, encoding="unic")

            # Charger et ajuster le QR code
            qr_image = Image.open(qrcode.image.path)
            qr_image = qr_image.resize((260, 260))
            et_image.paste(qr_image, (et_image.width - qr_image.width - 570, et_image.height - qr_image.height - 475))

            # Ajouter le texte
            draw = ImageDraw.Draw(et_image)
            draw.text((1066, 720), f"{numero}", font=font, fill="black")

            # Sauvegarder l'image
            buffer = BytesIO()
            et_image.save(buffer, format="PNG")
            buffer.seek(0)

            file_name = f"etiquette_levage_{client.name}_{site.name}_{numero}.png"
            return ContentFile(buffer.getvalue(), file_name)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'étiquette de levage: {str(e)}", exc_info=True)
            return None

    def _generate_thermographique_etiquette(self, numero, client, site, qrcode):
        """
        Génère une étiquette pour l'inspection thermographique.
        """
        try:
            # Charger l'image de base
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'thermographique2.png')
            if not os.path.exists(base_image_path):
                logger.error(f"Image de base introuvable: {base_image_path}")
                return None
                
            et_image = Image.open(base_image_path)
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')
            
            # Vérifier si le fichier de police existe
            if not os.path.exists(font_path):
                logger.warning(f"Police introuvable: {font_path}. Utilisation de la police par défaut.")
                font = ImageFont.load_default()
                font2 = ImageFont.load_default()
            else:
                font = ImageFont.truetype(font_path, 20, encoding="unic")
                font2 = ImageFont.truetype(font_path, 35, encoding="unic")

            # Charger et ajuster le QR code
            qr_image = Image.open(qrcode.image.path)
            qr_image = qr_image.resize((230, 230))
            et_image.paste(qr_image, (et_image.width - qr_image.width - 145, et_image.height - qr_image.height - 430))

            # Ajouter le texte
            draw = ImageDraw.Draw(et_image)
            draw.text((690, 370), f"KES_VERIF_THERMO_{numero}", font=font, fill="#1866fc")
            draw.text((790, 680), f"{numero}", font=font2, fill="#1866fc")
            
            # Calculer la taille en pixels pour 9cm x 9cm (à 96 DPI)
            size_in_pixels = (340, 340)  # 9cm = environ 340 pixels à 96 DPI
            
            # Redimensionner l'image finale
            et_image = et_image.resize(size_in_pixels, Image.LANCZOS)


            # Sauvegarder l'image
            buffer = BytesIO()
            et_image.save(buffer, format="TIFF", dpi=(96, 96))
            buffer.seek(0)

            file_name = f"etiquette_thermo_{client.name}_{site.name}_{numero}.tif"
            return ContentFile(buffer.getvalue(), file_name)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'étiquette thermographique: {str(e)}", exc_info=True)
            return None

    def _generate_electrique_etiquette(self, numero, client, site, qrcode):
        """
        Génère une étiquette pour l'inspection électrique.
        """
        try:
            # Charger l'image de base
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'electrique2.tif')
            if not os.path.exists(base_image_path):
                logger.error(f"Image de base introuvable: {base_image_path}")
                return None
                
            et_image = Image.open(base_image_path)
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')
            
            # Vérifier si le fichier de police existe
            if not os.path.exists(font_path):
                logger.warning(f"Police introuvable: {font_path}. Utilisation de la police par défaut.")
                font = ImageFont.load_default()
                font2 = ImageFont.load_default()
                font_client_text = ImageFont.load_default()
            else:
                font = ImageFont.truetype(font_path, 21, encoding="unic")
                font2 = ImageFont.truetype(font_path, 27, encoding="unic")
                
                # Texte du client avec ajustement dynamique de la taille
                text_client = f"{client.name} {site.name} {numero}"
                font_client_text = get_font_for_text(text_client, 700, font_path, 40)

            # Charger et ajuster le QR code
            qr_image = Image.open(qrcode.image.path)
            qr_image = qr_image.resize((340, 340))
            et_image.paste(qr_image, (et_image.width - qr_image.width - 120, et_image.height - qr_image.height - 480))

            # Ajouter le texte
            draw = ImageDraw.Draw(et_image)
            draw.text((500, 310), f"{client.name} {site.name} {numero}", font=font_client_text, fill="black")
            draw.text((1345, 780), f"KES_VERIF_ELEC_{numero}", font=font2, fill="black")
            
            
            # Sauvegarder l'image
            buffer = BytesIO()
            et_image.save(buffer, format="TIFF")
            buffer.seek(0)

            file_name = f"etiquette_verif_elec_{client.name}_{site.name}_{numero}.tif"
            return ContentFile(buffer.getvalue(), file_name)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'étiquette électrique: {str(e)}", exc_info=True)
            return None

    def _generate_extincteur_etiquette(self, numero, client, site, qrcode):
        """
        Génère une étiquette pour l'inspection d'extincteur.
        """
        try:
            # Charger l'image de base
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'Extincteur.png')
            if not os.path.exists(base_image_path):
                logger.error(f"Image de base introuvable: {base_image_path}")
                return None
                
            et_image = Image.open(base_image_path)
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')
            
            # Vérifier si le fichier de police existe
            if not os.path.exists(font_path):
                logger.warning(f"Police introuvable: {font_path}. Utilisation de la police par défaut.")
                font = ImageFont.load_default()
            else:
                font = ImageFont.truetype(font_path, 70, encoding="unic")

            # Charger et ajuster le QR code
            qr_image = Image.open(qrcode.image.path)
            qr_image = qr_image.resize((580, 580))
            et_image.paste(qr_image, (et_image.width - qr_image.width - 1130, et_image.height - qr_image.height - 970))

            # Ajouter le texte centré
            draw = ImageDraw.Draw(et_image)
            reference_point = (2180, 1490)
            text = f"{numero}"
            draw_centered_text(draw, text, font, reference_point, fill="black")

            # Sauvegarder l'image
            buffer = BytesIO()
            et_image.save(buffer, format="PNG")
            buffer.seek(0)

            file_name = f"etiquette_extincteur_{client.name}_{site.name}_{numero}.png"
            return ContentFile(buffer.getvalue(), file_name)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'étiquette d'extincteur: {str(e)}", exc_info=True)
            return None