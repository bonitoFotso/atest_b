# inspections/models.py

import uuid
from django.db import models
from apps.geography.models import Site
from apps.clients.models import Client, Affaire
from apps.documents.models import QRCode, Dossier
from django.contrib.auth import get_user_model

User = get_user_model()

class InspectionType(models.Model):
    LEVAGE = 'levage'
    THERMOGRAPHIQUE = 'thermographique'
    ELECTRIQUE = 'electrique'
    EXTINCTEUR = 'extincteur'

    INSPECTION_TYPE_CHOICES = [
        (LEVAGE, 'Levage'),
        (THERMOGRAPHIQUE, 'Thermographique'),
        (ELECTRIQUE, 'Electrique'),
        (EXTINCTEUR, 'Extincteur')
    ]

    name = models.CharField(
        max_length=255,
        choices=INSPECTION_TYPE_CHOICES,
        default=LEVAGE,
    )

    def __str__(self):
        return self.get_name_display()


class LotEtiquette(models.Model):
    total = models.IntegerField()
    inspectionType = models.ForeignKey(InspectionType, on_delete=models.CASCADE, related_name='lots')
    date_creation = models.DateTimeField(auto_now_add=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='lots')

    def __str__(self):
        return f"Lot {self.total} - {self.site.name} ({self.inspectionType.name})"

def generate_etiquette_image_path(instance, filename):
    return f'etiquettes/{instance.client.name}/{instance.site.name}/{instance.inspectionType}/{filename}'

class Etiquette(models.Model):
    inspectionType = models.ForeignKey(InspectionType, on_delete=models.CASCADE, related_name='etiquettes')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='etiquettes')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='etiquettes')
    numero = models.IntegerField()
    qrcode = models.ForeignKey('documents.QRCode', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=generate_etiquette_image_path, null=True, blank=True)
    isAssigned = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['client', 'site', 'inspectionType', 'numero'], name='unique_numero_per_site_inspection')
        ]
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['site']),
            models.Index(fields=['client']),
            models.Index(fields=['inspectionType']),
        ]

    def __str__(self):
        return f"Etiquette {self.numero} - Client: {self.client.name}, Site: {self.site.name}, Inspection: {self.inspectionType.name}"

class Rapport(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reports')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='reports')
    inspectionType = models.ForeignKey(InspectionType, on_delete=models.CASCADE)
    etiquette = models.ForeignKey(Etiquette, null=True, blank=True, on_delete=models.SET_NULL)
    qrcode = models.ForeignKey('documents.QRCode', on_delete=models.SET_NULL, null=True, blank=True)
    date_inspection = models.DateField()
    numero_rapport = models.CharField(max_length=50)
    business = models.ForeignKey(Affaire, on_delete=models.CASCADE, related_name='reports')
    fichier = models.FileField(upload_to='rapports/')
    dossier = models.ForeignKey('documents.Dossier', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.numero_rapport

class ArcFlashLabel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='arcflash_labels')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='arcflash_labels')
    cabinet_number = models.CharField(max_length=255, verbose_name="N° Armoire / Coffret")
    repere = models.CharField(max_length=255, verbose_name="Repère")
    network_voltage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tension du réseau (V)")
    gloves_class = models.CharField(max_length=50, verbose_name="Classe des gants")
    protection_distance = models.CharField(max_length=50, verbose_name="Distance de protection (mm)")
    max_energy = models.CharField(max_length=50, verbose_name="Énergie maximale (Cal/cm²)")
    incident_energy = models.CharField(max_length=50, verbose_name="Énergie incidente (Cal/cm²)")
    working_distance = models.CharField(max_length=50, verbose_name="Distance de travail (mm)")
    ppe_category = models.CharField(max_length=50, verbose_name="Catégorie EPI selon NFPA 70E")
    ik3max = models.CharField(max_length=50, verbose_name="Ik3max (kA)")
    inspection_date = models.DateField(verbose_name="Date d'inspection", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    qrcode = models.ForeignKey('documents.QRCode', on_delete=models.CASCADE, null=True, blank=True)
    fichier = models.FileField(upload_to='ark_flash/')
    dossier = models.ForeignKey('documents.Dossier', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"ArcFlashLabel {self.cabinet_number} - {self.repere}"

    class Meta:
        verbose_name = "Étiquette Arc Flash"
        verbose_name_plural = "Étiquettes Arc Flash"
        ordering = ['created_at']
