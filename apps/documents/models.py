# documents/models.py

import uuid
from django.db import models

class QRCode(models.Model):
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    image = models.ImageField(upload_to='qr_codes/')
    url = models.URLField(max_length=500)
    numero = models.CharField(max_length=50)

    def __str__(self):
        return self.url

class Dossier(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='enfants', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Fichier(models.Model):
    FICHIER_TYPE = [
        ('Rapport', 'Rapport'),
        ('Certificat', 'Certificat'),
        ('Etiquette', 'Etiquette'),
        ('QRCode', 'QRCode'),
    ]
    dossier = models.ForeignKey(Dossier, related_name='fichiers', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='fichiers/')
    type = models.CharField(max_length=50, choices=FICHIER_TYPE)
    date_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
