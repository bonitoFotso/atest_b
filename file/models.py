from django.db import models
from django.contrib.auth.models import User


# Modèle pour les rapports
class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


# Modèle pour les sites
class Site(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.client.name})"


# Modèle pour les documents
class Document(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='documents/')
    qrcode = models.OneToOneField("Qrcode", on_delete=models.CASCADE, related_name="qrcode")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()

    def __str__(self):
        return self.title


# Modèle pour les certificats
class Certificate(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='certificates')
    file = models.FileField(upload_to='certificates/')
    qrcode = models.OneToOneField("Qrcode", on_delete=models.CASCADE, related_name="qrcode")
    title = models.CharField(max_length=255)
    issued_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.client.name})"


# Modèle pour les rapports
class Report(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='reports')
    file = models.FileField(upload_to='reports/')
    qrcode = models.OneToOneField("Qrcode", on_delete=models.CASCADE, related_name="qrcode")
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.site.name})"


from django.db import models
from django.utils import timezone
import segno
from io import BytesIO
from django.core.files import File


class Certificat(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    date_emission = models.DateField(default=timezone.now)

    # autres champs nécessaires pour le certificat

    def __str__(self):
        return self.nom


class Rapport(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    date_inspection = models.DateField(default=timezone.now)

    # autres champs nécessaires pour le rapport

    def __str__(self):
        return self.nom


class Qrcode(models.Model):
    certificat = models.OneToOneField(Certificat, on_delete=models.CASCADE, null=True, blank=True)
    rapport = models.OneToOneField(Rapport, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='qrcodes/', blank=True)

    def save(self, *args, **kwargs):
        qr_data = self.get_qr_data()
        qr = segno.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, kind='png')
        file_name = f'qrcode-{self.id}.png'
        self.image.save(file_name, File(buffer), save=False)
        super().save(*args, **kwargs)

    def get_qr_data(self):
        if self.certificat:
            return f'Certificat: {self.certificat.nom} - {self.certificat.description}'
        elif self.rapport:
            return f'Rapport: {self.rapport.nom} - {self.rapport.description}'
        return ''

    def __str__(self):
        return f'Qrcode pour {self.certificat or self.rapport}'


class Fichier(models.Model):
    fichier = models.FileField(upload_to='fichiers/')
    certificat = models.ForeignKey(Certificat, on_delete=models.CASCADE, null=True, blank=True)
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.fichier.name
