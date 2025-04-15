from django.contrib.auth.models import User
from django.db import models
import uuid

import uuid
import segno
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
from django.db import models
from django.utils.text import slugify




# Modèle Client
class Client(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', related_name='subfolders', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


# Modèle Site
class Site(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} ({self.client.name})"


# Modèle Type d'Inspection
class InspectionType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Modèle Lot d'Étiquettes
class LotEtiquette(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='lots')
    inspection_type = models.ForeignKey(InspectionType, on_delete=models.CASCADE, related_name='lots')
    date_creation = models.DateTimeField(auto_now_add=True)
    total_etiquettes = models.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.inspectionType = None

    def __str__(self):
        return f"Lot {self.id} - {self.site.name} ({self.inspection_type.name})"


# Modèle QR Code
class QRCode(models.Model):
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    url = models.URLField(max_length=500)

    def __str__(self):
        return str(self.code)


class Inspecteur(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


# Modèle Étiquette
class Etiquette(models.Model):
    lot = models.ForeignKey(LotEtiquette, on_delete=models.CASCADE, related_name='etiquettes')
    numero = models.CharField(max_length=50, unique=True)
    qr_code = models.OneToOneField(QRCode, on_delete=models.CASCADE, related_name='etiquette')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        year_folder, _ = Folder.objects.get_or_create(name=str(self.lot.date_creation.year), parent=None)
        rapport_folder, _ = Folder.objects.get_or_create(name='rapports', parent=year_folder)
        client_folder, _ = Folder.objects.get_or_create(name=slugify(self.lot.site.client.name), parent=rapport_folder)
        site_folder, _ = Folder.objects.get_or_create(name=slugify(self.lot.site.name), parent=client_folder)
        inspectiontype_folder, _ = Folder.objects.get_or_create(name=slugify(self.lot.inspectionType.name),
                                                                parent=site_folder)
        numero, _ = Folder.objects.get_or_create(name=slugify(f"{self.lot.inspectionType} {self.numero}"),
                                                 parent=inspectiontype_folder)

        # File.objects.get_or_create(name=self.qr_code, folder=numero, defaults={'file': self.qr_code})

    def __str__(self):
        return f"Étiquette {self.numero} - Lot {self.lot.id}"


# Modèle Rapport
class Rapport(models.Model):
    inspection_type = models.ForeignKey(InspectionType, on_delete=models.CASCADE, related_name='rapports')
    file = models.FileField(upload_to='rapports/', blank=True, null=True)
    date_inspection = models.DateTimeField()
    inspecteurs = models.ManyToManyField(Inspecteur, related_name='rapports')  # Inspecteurs liés à un rapport
    etiquette = models.OneToOneField(Etiquette, related_name='rapports', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            # Create the file link

            file_url = f"{settings.BASE_URL}/media/rapports/{self.file.name}"
            file_link = FileLink.objects.create(file_url=file_url)
            self.file_link = file_link
            super().save(*args, **kwargs)

            # Create folder structure
            year_folder, _ = Folder.objects.get_or_create(name=str(self.dateInspection.year), parent=None)
            rapport_folder, _ = Folder.objects.get_or_create(name='rapports', parent=year_folder)
            client_folder, _ = Folder.objects.get_or_create(name=slugify(self.site.client.name), parent=rapport_folder)
            site_folder, _ = Folder.objects.get_or_create(name=slugify(self.site.name), parent=client_folder)
            inspectiontype_folder, _ = Folder.objects.get_or_create(name=slugify(self.inspectionType.name),
                                                                    parent=site_folder)
            folder, _ = Folder.objects.get_or_create(name=self.name, parent=inspectiontype_folder)
            file_instance, _ = File.objects.get_or_create(name=self.name, folder=folder,
                                                          defaults={'file': self.file, 'rapport': self})

            # Generate the QR code with the URL to the file
            file_uuid = file_link.uuid
            url_uuid = f"{settings.BASE_URL}/rapports/{file_uuid}/"

            qr = segno.make(url_uuid)
            qr_bytes = BytesIO()
            qr.save(qr_bytes, kind='png')

            # Save the QR code image to the QRCode model
            qr_filename = f"qr_{self.pk}.png"
            qr_code_instance = QRCode.objects.create(
                rapport=self,
                url=file_url,
                image=ContentFile(qr_bytes.getvalue(), qr_filename)
            )
            self.qr_code = qr_code_instance
    def __str__(self):
        return f"Rapport {self.id} - {self.inspection_type.name} ({self.etiquette.lot.site.name})"
