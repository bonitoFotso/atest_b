from django.db import models

class Employeur(models.Model):
    nom = models.CharField("Nom de l'employeur", max_length=100)
    adresse = models.CharField("Adresse de l'employeur", max_length=100, null=True, blank=True)
    logo = models.ImageField("Logo de l'employeur", upload_to='logos/', null=True, blank=True)

    def __str__(self):
        return self.nom


class Responsable(models.Model):
    nom = models.CharField("Nom du responsable", max_length=100)
    prenom = models.CharField("Prénom du responsable", max_length=100, null=True, blank=True)
    fonction = models.CharField("Fonction du responsable", max_length=100, null=True, blank=True)
    reference_employeur = models.CharField("Référence du responsable", max_length=100, null=True, blank=True)
    employeur = models.ForeignKey(Employeur, on_delete=models.CASCADE, related_name="responsables")

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.employeur.nom}"


class Participant(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    sexe = models.CharField("Sexe", max_length=1, choices=SEXE_CHOICES)
    nom = models.CharField("Nom du participant", max_length=255)
    prenom = models.CharField("Prénom du participant", max_length=255)
    fonction = models.CharField("Fonction du participant", max_length=100, null=True, blank=True)
    date_naissance = models.DateField("Date de naissance")
    lieu_naissance = models.CharField("Lieu de naissance", max_length=255)
    numero_cni = models.CharField("Numéro de CNI", max_length=50)
    employeur = models.ForeignKey(Employeur, on_delete=models.CASCADE, related_name="participants")

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Habilitation(models.Model):
    reference = models.CharField("Référence de l'habilitation", max_length=100)
    ville = models.CharField("Ville de formation", max_length=255, blank=True, null=True)
    duree_formation = models.CharField("Durée de la formation", max_length=50, blank=True, null=True)
    symboles_requis = models.CharField("Symboles requis", max_length=255, blank=True, null=True)
    lieu_formation = models.CharField("Lieu de la formation", max_length=255)
    date = models.DateField("Date de début de la formation")
    periode_validite = models.CharField("Période de validité", max_length=50)
    titre_habilitation = models.CharField("Titre de l'habilitation", max_length=100)
    installations_concernees = models.CharField("Installations concernées", max_length=255, blank=True, null=True)
    instructions_supplementaires = models.TextField("Instructions supplémentaires", blank=True, null=True)
    numero_titre = models.CharField("Numéro de titre", max_length=100, blank=True, null=True)
    responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE, related_name="habilitations")

    def __str__(self):
        return f"Habilitation {self.reference} - {self.titre_habilitation}"


class Inscription(models.Model):
    habilitation = models.ForeignKey(Habilitation, on_delete=models.CASCADE, related_name="inscriptions")
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="inscriptions")

    def __str__(self):
        return f"Inscription de {self.participant.nom} {self.participant.prenom} pour {self.habilitation.reference}"
