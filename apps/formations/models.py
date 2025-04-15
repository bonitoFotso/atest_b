
from django.db import models

class Formation(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date_debut = models.DateField()
    date_fin = models.DateField()

    def __str__(self):
        return self.titre


class Participant(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    fonction = models.CharField(max_length=255)
    poste_affectation = models.CharField(max_length=255)
    nom_responsable = models.CharField(max_length=255, null=True, blank=True)
    fonction_emp = models.CharField(max_length=255, null=True, blank=True)
    prenom_resp = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ImageField(upload_to="photos", null=True, blank=True)
    formation = models.ForeignKey('Formation', on_delete=models.CASCADE, related_name='participants')

    def __str__(self):
        return f"{self.nom} {self.prenom}"

