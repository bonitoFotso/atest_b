# certifications/models.py

from django.db import models
from apps.documents.models import QRCode, Dossier
from apps.habilitations.models import Participant


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




class Certificat(models.Model):
    name = models.CharField(max_length=255)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    qrcode = models.ForeignKey(QRCode, on_delete=models.CASCADE, null=True, blank=True)
    fichier = models.FileField(upload_to='certificats/', null=True, blank=True)
    dossier = models.ForeignKey(Dossier, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Certificat {self.name} - {self.participant.nom} {self.participant.prenom}"



