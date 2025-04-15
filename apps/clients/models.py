# clients/models.py
from django.core.exceptions import ValidationError
from django.db import models
from apps.geography.models import Site
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_client_codes():
    clients = Client.objects.all()

    for client in clients:
        if not client.code:  # Si le client n'a pas de code, le générer
            base_code = client.name[:3].upper()
            existing_codes = Client.objects.filter(code__startswith=base_code).count()
            client.code = f"{base_code}{existing_codes + 1:03d}"
            client.save()
            print(f"Code généré pour le client {client.name}: {client.code}")

class Statut(models.Model):
    status_name = models.CharField(max_length=45)

    def __str__(self):
        return self.status_name

class Client(models.Model):
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    logo = models.ImageField(upload_to='logo/', blank=True, null=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    nom_responsable = models.CharField(max_length=255, null=True, blank=True)
    fonction_emp = models.CharField(max_length=255, null=True, blank=True)
    prenom_resp = models.CharField(max_length=255, null=True, blank=True)
    sites = models.ManyToManyField(Site, through='ClientSite', related_name='clients')

    def save(self, *args, **kwargs):
        if not self.code:
            base_code = self.name[:3].upper()  # Utilisation des trois premières lettres du nom du client
            existing_codes = Client.objects.filter(code__startswith=base_code).count()
            self.code = f"{base_code}{existing_codes + 1:03d}"  # Génération d'un code comme "CIM001"
        super(Client, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"



class ClientSite(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    code = models.CharField(max_length=30, unique=True, blank=True, null=True)  # Code unique pour l'association client-site

    class Meta:
        unique_together = ('client', 'site')

    def save(self, *args, **kwargs):
        if not self.code:
            client_code = self.client.code
            city_code = self.site.city.name[:3].upper()  # Utilisation des trois premières lettres du nom de la ville
            count = ClientSite.objects.filter(client=self.client, site__city=self.site.city).count()
            self.code = f"{client_code}-{city_code}-{count + 1:02d}"  # Génération d'un code comme "CIM001-BON-01"
        super(ClientSite, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.client.name} - {self.site.name}"



class Affaire(models.Model):
    customer_representative_name = models.CharField(max_length=45, verbose_name="Nom du représentant client")
    customer_representative_function = models.CharField(max_length=45, verbose_name="Fonction du représentant client")
    status = models.ForeignKey(Statut, on_delete=models.CASCADE, verbose_name="Statut")
    creer_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur qui a créé l'affaire")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='businesses', verbose_name="Client")
    sites = models.ManyToManyField(Site, related_name='businesses', verbose_name="Sites")

    def __str__(self):
        return f"Affaire - {self.client.name} - {self.customer_representative_name}"

    class Meta:
        verbose_name = "Affaire"
        verbose_name_plural = "Affaires"
