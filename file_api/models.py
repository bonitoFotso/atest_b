import uuid

from django.core.exceptions import ValidationError
from django.db import models

from auths.models import User


class Region(models.Model):
    region_name = models.CharField(max_length=45)

    def __str__(self):
        return self.region_name

class City(models.Model):
    name = models.CharField(max_length=45)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name

class Site(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.city.name})"

class Client(models.Model):
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    sites = models.ManyToManyField(Site, related_name='clients')


    def __str__(self):
        return self.name



class Affaire(models.Model):
    customer_representative_name = models.CharField(max_length=45, verbose_name="Nom du représentant client")
    customer_representative_function = models.CharField(max_length=45, verbose_name="Fonction du représentant client")
    status = models.ForeignKey('Statut', on_delete=models.CASCADE, verbose_name="Statut")
    creer_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur qui a cree l'affaire")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='businesses', verbose_name="Client")
    sites = models.ManyToManyField(Site, related_name='businesses', verbose_name="Sites")

    def __str__(self):
        return f"Affaire - {self.client.name} - {self.customer_representative_name}"

    def clean(self):
        # Vérifier que tous les sites associés appartiennent au client
        invalid_sites = self.sites.exclude(id__in=self.client.sites.values_list('id', flat=True))
        if invalid_sites.exists():
            site_names = ', '.join(invalid_sites.values_list('name', flat=True))
            raise ValidationError(
                f"Les sites suivants ne sont pas associés au client {self.client.name} : {site_names}")

    class Meta:
        verbose_name = "Affaire"
        verbose_name_plural = "Affaires"


class Statut(models.Model):
    status_name = models.CharField(max_length=45)

    def __str__(self):
        return self.status_name

class InspectionType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name



class QRCode(models.Model):
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    image = models.ImageField(upload_to='qr_codes/')
    url = models.URLField(max_length=500)
    numero = models.CharField(max_length=50)

    def __str__(self):
        return self.url


class LotEtiquette(models.Model):
    total = models.IntegerField()
    inspectionType = models.ForeignKey(InspectionType, on_delete=models.CASCADE, related_name='lots')
    date_creation = models.DateTimeField(auto_now_add=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='lots')

    def __str__(self):
        return f"Lot {self.total} - {self.site.name} ({self.inspectionType.name})"


def generate_etiquette_image_path(instance, filename):
    """
    Génère dynamiquement le chemin de téléchargement de l'image de l'étiquette en fonction du client, du site et du lot.
    :param instance: Instance du modèle Etiquette.
    :param filename: Nom original du fichier.
    :return: Chemin de téléchargement.
    """
    return f'etiquettes/{instance.site.client.name}/{instance.site.name}/{instance.inspectionType}/{filename}'



class Etiquette(models.Model):
    inspectionType = models.ForeignKey(InspectionType, on_delete=models.CASCADE, related_name='etiquettes')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='etiquettes')
    numero = models.IntegerField()
    qrcode = models.ForeignKey(QRCode, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=generate_etiquette_image_path, null=True, blank=True)
    isAssigned = models.BooleanField(default=False)

    class Meta:
        # Ajout d'une contrainte d'unicité sur (site, inspectionType, numero)
        constraints = [
            models.UniqueConstraint(fields=['site', 'inspectionType', 'numero'], name='unique_numero_per_site_inspection')
        ]

        # Indexation des champs pour des recherches plus rapides
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['site']),
            models.Index(fields=['inspectionType']),
        ]

    def __str__(self):
        return f"Etiquette {self.numero} - Site: {self.site.name}, Inspection: {self.inspectionType.name}"



class Rapport(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    inspectionType = models.ForeignKey(InspectionType, on_delete=models.CASCADE)
    etiquette = models.ForeignKey(Etiquette, null=True, blank=True, on_delete=models.SET_NULL)
    qrcode = models.ForeignKey(QRCode, on_delete=models.SET_NULL, null=True, blank=True)
    date_inspection = models.DateField()
    numero_rapport = models.CharField(max_length=50)
    business = models.ForeignKey(Affaire, on_delete=models.CASCADE, related_name='reports')
    fichier = models.FileField(upload_to='rapports/')
    dossier = models.ForeignKey('Dossier', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.numero_rapport



class CertificaType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Session(models.Model):
    MOIS_CHOICES = [
        ('Janvier', 'Janvier'),
        ('Février', 'Février'),
        ('Mars', 'Mars'),
        ('Avril', 'Avril'),
        ('Mai', 'Mai'),
        ('Juin', 'Juin'),
        ('Juillet', 'Juillet'),
        ('Août', 'Août'),
        ('Septembre', 'Septembre'),
        ('Octobre', 'Octobre'),
        ('Novembre', 'Novembre'),
        ('Décembre', 'Décembre'),
    ]

    mois = models.CharField(max_length=11, choices=MOIS_CHOICES)
    annee = models.PositiveIntegerField()
    certificaType = models.ForeignKey(CertificaType, on_delete=models.CASCADE, related_name="sessions")

    def __str__(self):
        return f"Session {self.mois}/{self.annee} - {self.certificaType.name}"


class Participant(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)

    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=255)
    numero_cni = models.CharField(max_length=50)
    entreprise = models.CharField(max_length=255)
    poste = models.CharField(max_length=255)
    sessions = models.ManyToManyField(Session, related_name="participants")

    def __str__(self):
        return f"{self.nom} {self.prenom}"



class Certificat(models.Model):
    name = models.CharField(max_length=255)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    qrcode = models.ForeignKey(QRCode, on_delete=models.CASCADE, null=True, blank=True)
    fichier = models.FileField(upload_to='certificats/', null=True, blank=True)
    dossier = models.ForeignKey('Dossier', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Certificat {self.name} - {self.participant.nom} {self.participant.prenom}"




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




class ArcFlashLabel(models.Model):
    # Identifiant unique pour chaque étiquette
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    # Informations sur l'équipement
    cabinet_number = models.CharField(max_length=255, verbose_name="N° Armoire / Coffret")
    repere = models.CharField(max_length=255, verbose_name="Repère")  # Texte dans le champ "Repère"

    # Données techniques liées à la protection et à l'énergie
    network_voltage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tension du réseau (V)")
    gloves_class = models.CharField(max_length=50, verbose_name="Classe des gants")
    protection_distance = models.CharField(max_length=50, verbose_name="Distance de protection (mm)")
    max_energy = models.CharField(max_length=50, verbose_name="Énergie maximale (Cal/cm²)")
    incident_energy = models.CharField(max_length=50, verbose_name="Énergie incidente (Cal/cm²)")
    working_distance = models.CharField(max_length=50, verbose_name="Distance de travail (mm)")
    ppe_category = models.CharField(max_length=50, verbose_name="Catégorie EPI selon NFPA 70E")
    ik3max = models.CharField(max_length=50, verbose_name="Ik3max (kA)")

    # Informations supplémentaires
    inspection_date = models.DateField(verbose_name="Date d'inspection", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    qrcode = models.ForeignKey(QRCode, on_delete=models.CASCADE, null=True, blank=True)
    fichier = models.FileField(upload_to='ark_flash/')
    dossier = models.ForeignKey('Dossier', null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return f"ArcFlashLabel {self.cabinet_number} - {self.repere}"

    class Meta:
        verbose_name = "Étiquette Arc Flash"
        verbose_name_plural = "Étiquettes Arc Flash"
        ordering = ['created_at']

