from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Max
from .models import Etiquette, QRCode
from .serializers import EtiquetteAutoCreateSerializer
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
import os
import uuid


class GenerateEtiquettesView(APIView):
    """
    Vue pour générer automatiquement des étiquettes pour un site et un type d'inspection donnés,
    ainsi que des fichiers d'étiquettes en fonction du type d'inspection.
    """

    def post(self, request, *args, **kwargs):
        serializer = EtiquetteAutoCreateSerializer(data=request.data)

        if serializer.is_valid():
            site = serializer.validated_data['site']
            inspectionType = serializer.validated_data['inspectionType']
            nombre = serializer.validated_data['nombre']

            # Trouver le dernier numéro déjà utilisé pour ce site et ce type d'inspection
            dernier_numero = Etiquette.objects.filter(site=site, inspectionType=inspectionType).aggregate(
                max_numero=Max('numero')
            )['max_numero']

            # Si aucune étiquette n'existe encore, commence à 1, sinon continue à partir du dernier numéro + 1
            numero_debut = (dernier_numero or 0) + 1

            etiquettes = []
            for i in range(numero_debut, numero_debut + nombre):
                numero = numero_debut + i
                # Générer un QRCode pour chaque étiquette
                qr_code = self.generate_qr_code(numero, site, inspectionType)

                # Générer l'image de l'étiquette selon le type d'inspection
                etiquette_image = self.generate_etiquette_image(inspectionType.name, numero, site, qr_code)

                if etiquette_image is None:
                    return Response({
                        "error": f"Erreur lors de la génération de l'image pour l'étiquette {numero}."
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Créer l'étiquette
                etiquette = Etiquette.objects.create(
                    site=site,
                    inspectionType=inspectionType,
                    numero=numero,
                    qrcode=qr_code,
                    image=etiquette_image,
                    isAssigned=False
                )
                etiquettes.append(etiquette)

            # Retourner une réponse indiquant que les étiquettes ont été créées avec succès
            return Response({
                "message": f"{nombre} étiquettes créées avec succès à partir du numéro {numero_debut}.",
                "etiquettes_created": nombre
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_qr_code(self, numero, site, inspection_type):
        """
        Générer un QR Code et le sauvegarder sous forme d'image.
        """
        try:
            qr_uuid = uuid.uuid4()
            qr_url = f"{settings.BASE_URL}/rapport/{qr_uuid}/"

            # Génération du QR code
            qr = segno.make(qr_url)
            qr_bytes = BytesIO()
            qr.save(qr_bytes, kind='png', border=0)

            # Créer un nom de fichier pour le QR code
            qr_filename = os.path.join(f"{site.client.name}/{site.name}/{inspection_type.name}",
                                       f"qr_code_{numero}.png")

            # Créer l'objet QRCode en base de données
            qr_code = QRCode.objects.create(
                code=qr_uuid,
                url=qr_url,
                image=ContentFile(qr_bytes.getvalue(), qr_filename),
                numero=f"{site.client.name}_{site.name}_{numero}"
            )
            return qr_code
        except Exception as e:
            print(f"Erreur lors de la génération du QR code : {e}")
            return None

    def generate_etiquette_image(self, inspection_type_name, numero, site, qrcode):
        """
        Génère l'image d'une étiquette en fonction du type d'inspection (levage, thermographique, électrique).
        """
        inspection_type_name = inspection_type_name.lower()

        if inspection_type_name == 'levage':
            return self.generate_levage_etiquette(numero, site, qrcode)
        elif inspection_type_name == 'thermographique':
            return self.generate_thermographique_etiquette(numero, site, qrcode)
        elif inspection_type_name == 'electrique':
            return self.generate_electrique_etiquette(numero, site, qrcode)
        else:
            raise ValueError(f"Type d'inspection '{inspection_type_name}' non pris en charge.")

    def generate_levage_etiquette(self, numero, site, qrcode):
        """
        Génère une étiquette pour l'inspection de levage.
        """
        return self._generate_generic_etiquette('levage_template.png', numero, site, qrcode)

    def generate_thermographique_etiquette(self, numero, site, qrcode):
        """
        Génère une étiquette pour l'inspection thermographique.
        """
        return self._generate_generic_etiquette('thermo_template.png', numero, site, qrcode)

    def generate_electrique_etiquette(self, numero, site, qrcode):
        """
        Génère une étiquette pour l'inspection électrique.
        """
        return self._generate_generic_etiquette('electrique_template.png', numero, site, qrcode)

    def _generate_generic_etiquette(self, template_filename, numero, site, qrcode):
        """
        Génération générique d'une étiquette avec une image de base et un QR code.
        """
        try:
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', template_filename)
            et_image = Image.open(base_image_path)
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')

            # Charger et ajuster la taille du QR code
            qr_image = Image.open(qrcode.image.path)
            qr_image = qr_image.resize((150, 150))
            et_image.paste(qr_image, (50, 50))

            # Ajouter le texte personnalisé
            draw = ImageDraw.Draw(et_image)
            font = ImageFont.truetype(font_path, 20)
            draw.text((200, 50), f"Numéro: {numero}", font=font, fill="black")
            draw.text((200, 150), f"Site: {site.name}", font=font, fill="black")

            # Sauvegarder l'image dans un buffer
            buffer = BytesIO()
            et_image.save(buffer, format="PNG")
            buffer.seek(0)

            # Retourner l'image sous forme de fichier
            file_name = f"etiquette_{numero}.png"
            return ContentFile(buffer.getvalue(), file_name)
        except Exception as e:
            print(f"Erreur lors de la génération de l'étiquette : {e}")
            return None
