import os
from rest_framework import generics, status
from rest_framework.response import Response

from ..arc_flash.views import get_font_for_text
from ..models import LotEtiquette, Etiquette, QRCode
import uuid
from rest_framework.views import APIView

from django.conf import settings
import zipfile
from django.http import HttpResponse
import segno
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from .serializers import EtiquetteSerializer, EtiquetteAutoCreateSerializer
from django.db.models import Max


class EtiquetteListCreateView(generics.ListCreateAPIView):
    queryset = Etiquette.objects.all()
    serializer_class = EtiquetteSerializer

    def perform_create(self, serializer):
        # Custom logic during creation, if necessary
        serializer.save()

class EtiquetteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Etiquette.objects.all()
    serializer_class = EtiquetteSerializer


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
            numero_debut = dernier_numero + 1 if dernier_numero else 1
            print('nombre', dernier_numero)
            print('numero de debut',numero_debut)

            etiquettes = []
            zip_buffer = BytesIO()  # Buffer pour stocker le fichier ZIP
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for i in range(numero_debut, numero_debut + nombre):
                    numero = i

                    # Générer un QRCode pour chaque étiquette
                    qr_code = self.generate_qr_code(numero, site, inspectionType)

                    # Générer l'image de l'étiquette selon le type d'inspection
                    etiquette_image = self.generate_etiquette_image(inspectionType.name, numero, site, qr_code)
                    print('etiquette_image', etiquette_image)
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

                    # Ajouter l'étiquette au fichier ZIP
                    if etiquette.image:
                        zip_file.writestr(f"etiquette_{numero}.png", etiquette.image.read())

            zip_buffer.seek(0)

            # Créer la réponse HTTP avec le fichier ZIP
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="etiquettes_{site.name}_{inspectionType.name}.zip"'

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_qr_code(self, numero, site, inspection_type):
        # Générer l'URL du QR Code (adapté à votre logique métier)
        qr_uuid = uuid.uuid4()
        qr_url = f"{settings.BASE_URL}/rapport/{qr_uuid}/"

        # Utilisation de segno pour créer le QR Code
        qr = segno.make(qr_url)
        qr_bytes = BytesIO()
        qr.save(qr_bytes, kind='png', border=0)

        # Chemin dynamique pour stocker les QR codes
        qr_filename = os.path.join(f"{site.client.name}/{site.name}/{inspection_type.name}", f"qr_code_{numero}.png")

        # Créer le fichier QR code dans le modèle QRCode
        qr_code = QRCode.objects.create(
            code=qr_uuid,
            url=qr_url,
            image=ContentFile(qr_bytes.getvalue(), qr_filename),
            numero=f"{site.client.name}_{site.name}_{numero}"
        )
        return qr_code

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
        try:
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'levage.jpeg')
            et_image = Image.open(base_image_path)
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')

            # Charger et ajuster la taille du QR code
            qr_image = Image.open(qrcode.image.path)
            qr_image = qr_image.resize((155, 155))
            et_image.paste(qr_image, (et_image.width - qr_image.width - 345, et_image.height - qr_image.height - 290))

            # Ajouter le texte
            draw = ImageDraw.Draw(et_image)
            font = ImageFont.truetype(font_path, 20, encoding="unic")

            # Texte personnalisé
            draw.text((620, 420), f"{numero}", font=font, fill="black")

            # Sauvegarder l'image dans un buffer
            buffer = BytesIO()
            et_image.save(buffer, format="PNG")
            buffer.seek(0)

            # Retourner l'image sous forme de fichier
            file_name = f"etiquette_{numero}.png"
            return ContentFile(buffer.getvalue(), file_name)
        except Exception as e:
            print(f"Erreur lors de la génération de l'étiquette de levage : {e}")
            return None

    def generate_thermographique_etiquette(self, numero, site, qrcode):
        """
        Génère une étiquette pour l'inspection thermographique.
        """
        try:
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'thermographique.jpeg')
            et_image = Image.open(base_image_path)
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')

            # Charger et ajuster la taille du QR code
            qr_image = Image.open(qrcode.image.path)
            qr_image = qr_image.resize((230, 230))
            et_image.paste(qr_image, (et_image.width - qr_image.width - 145, et_image.height - qr_image.height - 430))

            # Ajouter le texte personnalisé
            draw = ImageDraw.Draw(et_image)
            font = ImageFont.truetype(font_path, 20, encoding="unic")
            font2 = ImageFont.truetype(font_path, 35, encoding="unic")

            draw.text((690, 370), f"KES_VERIF_THERMO_{numero}", font=font, fill="#1866fc")
            draw.text((790, 680), f"{numero}", font=font2, fill="#1866fc")

            # Sauvegarder l'image dans un buffer
            buffer = BytesIO()
            et_image.save(buffer, format="PNG")
            buffer.seek(0)

            # Retourner l'image sous forme de fichier
            file_name = f"etiquette_{numero}.png"
            return ContentFile(buffer.getvalue(), file_name)
        except Exception as e:
            print(f"Erreur lors de la génération de l'étiquette thermographique : {e}")
            return None

    def generate_electrique_etiquette(self, numero, site, qrcode):
        """
        Génère une étiquette pour l'inspection électrique.
        """
        try:
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'electrique.jpeg')
            et_image = Image.open(base_image_path)
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')

            # Charger et ajuster la taille du QR code
            qr_image = Image.open(qrcode.image.path)
            qr_image = qr_image.resize((150, 150))
            et_image.paste(qr_image, (et_image.width - qr_image.width - 40, et_image.height - qr_image.height - 160))

            # Ajouter le texte personnalisé
            draw = ImageDraw.Draw(et_image)
            font = ImageFont.truetype(font_path, 21, encoding="unic")
            font2 = ImageFont.truetype(font_path, 14, encoding="unic")

            text_client = f"{site.client.name} {site.name}  {numero}"
            font_client_text = get_font_for_text(text_client, 500, font_path, 21)
            draw.text((200, 112), f"{site.client.name} {site.name} {numero}", font=font_client_text, fill="black")
            draw.text((530, 285), f"KES_VERIF_ELEC_{numero}", font=font2, fill="black")

            # Sauvegarder l'image dans un buffer
            buffer = BytesIO()
            et_image.save(buffer, format="PNG")
            buffer.seek(0)

            # Retourner l'image sous forme de fichier
            file_name = f"etiquette_{numero}.png"
            return ContentFile(buffer.getvalue(), file_name)
        except Exception as e:
            print(f"Erreur lors de la génération de l'étiquette électrique : {e}")
            return None

class LotEtiquetteCreateView(generics.CreateAPIView):
    queryset = LotEtiquette.objects.all()
    serializer_class = EtiquetteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Créer le Lot d'Étiquettes
        lot = serializer.save()

        # Trouver la dernière étiquette pour ce site et ce type d'inspection
        last_etiquette = Etiquette.objects.filter(
            lot__site=lot.site,
            lot__inspectionType=lot.inspectionType
        ).order_by('numero').last()

        # Si aucune étiquette n'existe encore, commencer à 1, sinon continuer après la dernière
        start_numero = last_etiquette.numero + 1 if last_etiquette else 1

        # Dictionnaire pour associer chaque type d'inspection à sa méthode de génération d'étiquette
        generate_etiquette_function = {
            'electrique': self.generate_electrique_etiquette,
            'thermographique': self.generate_thermographique_etiquette,
            'levage': self.generate_levage_etiquette
        }

        # Vérifier si le type d'inspection a une méthode de génération associée
        inspection_type_key = lot.inspectionType.name.lower()  # Assurez-vous que le nom est en minuscules
        generate_etiquette = generate_etiquette_function.get(inspection_type_key)

        if not generate_etiquette:
            return Response({"detail": f"Type d'inspection '{inspection_type_key}' non pris en charge."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Générer automatiquement les étiquettes pour ce lot
        for numero in range(start_numero, start_numero + lot.total):
            # Générer le QR Code pour chaque étiquette
            qr_code = self.generate_qr_code(numero, lot.site, lot.inspectionType)

            # Générer l'image d'étiquette fusionnée avec le QR code
            etiquette_image = generate_etiquette(qr_code.image, numero, lot.site)

            # Créer l'étiquette
            Etiquette.objects.create(
                lot=lot,
                numero=numero,
                qrcode=qr_code,
                image=etiquette_image,
                isAssigned=False
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def generate_qr_code(self, numero, site, inspection_type):
        # Générer l'URL du QR Code (adapté à votre logique métier)
        qr_uuid = uuid.uuid4()
        qr_url = f"{settings.BASE_URL}/rapport/{qr_uuid}/"

        # Utilisation de segno pour créer le QR Code
        qr = segno.make(qr_url)
        qr_bytes = BytesIO()
        qr.save(qr_bytes, kind='png', scale=10,border=0)

        # Chemin dynamique pour stocker les QR codes
        qr_filename = os.path.join(f"{site.client.name}/{site.name}/{inspection_type.name}", f"qr_code_{numero}.png")

        # Créer le fichier QR code dans le modèle QRCode
        qr_code = QRCode.objects.create(
            code=qr_uuid,
            url=qr_url,
            image=ContentFile(qr_bytes.getvalue(), qr_filename),
            numero=f"{site.client.name}_{site.name}_{numero}"
        )
        return qr_code

    # Méthodes de génération d'étiquettes spécifiques à chaque type
    def generate_electrique_etiquette(self, qr_image_path, numero, site):
        return self._generate_etiquette_electrique(qr_image_path, numero, site)

    def generate_thermographique_etiquette(self, qr_image_path, numero, site):
        return self._generate_etiquette_thermographique(qr_image_path, numero )


    def generate_levage_etiquette(self, qr_image_path, numero, site):
        return self._generate_etiquette_levage(qr_image_path, numero)

    # Méthode générique pour générer une étiquette avec des dimensions et une image de base spécifiques
    def _generate_etiquette_levage(self, qr_image_path, numero):
        try:
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'levage.jpeg')
            et_image = Image.open(base_image_path)
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')

            # Charger et ajuster la taille du QR code
            qr_image = Image.open(qr_image_path.path)
            qr_image = qr_image.resize((155, 155))
            et_image.paste(qr_image, (et_image.width - qr_image.width - 345, et_image.height - qr_image.height - 290))

            # Ajouter le texte
            draw = ImageDraw.Draw(et_image)
            font = ImageFont.truetype(font_path, 20, encoding="unic")

            # Texte personnalisé
            draw.text((620, 420), f"{numero}", font=font, fill="black")

            # Sauvegarder l'image dans un buffer
            buffer = BytesIO()
            et_image.save(buffer, format="PNG")
            buffer.seek(0)

            # Retourner l'image sous forme de fichier
            file_name = f"levage/etiquette_{numero}.png"
            return ContentFile(buffer.getvalue(), file_name)

        except Exception as e:
            print(f"Erreur lors de la génération de l'étiquette levage : {e}")
            return None
    def _generate_etiquette_electrique(self, qr_image_path, numero, site,):
        try:
            base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'electrique.jpeg')
            et_image = Image.open(base_image_path)
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'arial.ttf')

            # Charger et ajuster la taille du QR code
            qr_image = Image.open(qr_image_path.path)
            qr_image = qr_image.resize((150, 150))
            et_image.paste(qr_image, (et_image.width - qr_image.width - 40, et_image.height - qr_image.height - 150))

            # Ajouter le texte
            draw = ImageDraw.Draw(et_image)
            font = ImageFont.truetype(font_path, 21, encoding="unic")
            font2 = ImageFont.truetype(font_path, 14, encoding="unic")

            # Texte personnalisé
            draw.text((200, 112), f"{site.client.name} {site.name} {numero}", font=font, fill="black")
            draw.text((530, 280), f"KES_VERIF_ELEC_{numero}", font=font2, fill="black")

            # Sauvegarder l'image dans un buffer
            buffer = BytesIO()
            et_image.save(buffer, format="PNG")
            buffer.seek(0)

            # Retourner l'image sous forme de fichier
            file_name = f"etiquette_{numero}_with_qrcode.png"
            return ContentFile(buffer.getvalue(), file_name)
        except Exception as e:
            print(f"Erreur lors de la génération de l'étiquette electrique : {e}")
            return None

    def _generate_etiquette_thermographique(self, qr_image_path, numero,):
            try:
                base_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'thermographique.jpeg')
                et_image = Image.open(base_image_path)
                font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'ARIALBD.TTF')
                print('thermo')

                # Charger et ajuster la taille du QR code
                qr_image = Image.open(qr_image_path.path)
                qr_image = qr_image.resize((230, 230))
                et_image.paste(qr_image,
                               (et_image.width - qr_image.width - 145, et_image.height - qr_image.height - 430))

                print('thermo 2')
                # Ajouter le texte
                draw = ImageDraw.Draw(et_image)
                font = ImageFont.truetype(font_path, 20, encoding="unic")
                font2 = ImageFont.truetype(font_path, 35, encoding="unic")
                print('thermo 3')

                # Texte personnalisé
                # draw.text((200, 112), f"{client_name} {site_name} {numero}", font=font, fill="black")
                draw.text((690, 370), f"KES_VERIF_THERMO_{numero}", font=font, fill="#1866fc")
                draw.text((790, 680), f"{numero}", font=font2, fill="#1866fc")
                # Sauvegarder l'image dans un buffer
                buffer = BytesIO()
                et_image.save(buffer, format="PNG")
                buffer.seek(0)

                # Retourner l'image sous forme de fichier
                file_name = f"thermographique/etiquette_{numero}.png"
                return ContentFile(buffer.getvalue(), file_name)

            except Exception as e:
                print(f"Erreur lors de la génération de l'étiquette thermo  : {e}")
                return None


class DownloadLotEtiquettesView(generics.GenericAPIView):
    """
    Vue pour télécharger toutes les étiquettes d'un lot sous forme de fichier ZIP.
    """
    queryset = LotEtiquette.objects.all()

    def get(self, request, *args, **kwargs):
        lot_id = kwargs.get('lot_id')
        try:
            # Récupérer le lot en fonction de son ID
            lot = LotEtiquette.objects.get(id=lot_id)
        except LotEtiquette.DoesNotExist:
            return HttpResponse(status=404, content="Lot non trouvé")

        # Créer un buffer en mémoire pour stocker le fichier ZIP
        buffer = BytesIO()

        # Créer un fichier ZIP dans le buffer
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            # Récupérer toutes les étiquettes du lot
            etiquettes = Etiquette.objects.filter(lot=lot)

            for etiquette in etiquettes:
                if etiquette.image:
                    # Ajouter chaque image d'étiquette au fichier ZIP
                    image_name = f"etiquette_{etiquette.numero}.png"
                    zip_file.writestr(image_name, etiquette.image.read())

        # Finaliser le fichier ZIP
        buffer.seek(0)

        # Créer une réponse HTTP pour envoyer le fichier ZIP
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{lot.site.client.name}_{lot.site.name}_{lot.inspectionType.name}_{lot.total}_etiquettes.zip"'

        return response
