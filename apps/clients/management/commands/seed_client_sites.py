from django.core.management.base import BaseCommand

from apps.clients.models import Client, ClientSite
from apps.geography.models import Site


class Command(BaseCommand):
    help = 'Associate clients with their respective sites using the intermediate model ClientSite'

    def handle(self, *args, **kwargs):
        # Dictionnaire contenant les clients et leurs sites respectifs
        associations = {
            "SCB": [
                "BONANJO", "VILLA DG", "OBALA", "EBOLOWA", "AMBAM", "BERTOUA",
                "MEINGANGA", "NGAOUNDERE", "GAROUA", "MAROUA", "YAGOUA", 
                "KOUSSERI", "BAFOUSSAM", "DSCHANG", "LIMBE"
            ],
            "SABC": [
                "CENTRE DE DISTRIBUTION", "BONANJO", "VILLA DG", "AKWA", 
                "CC-NDOKOTI", "BONABERI", "CED-NDOKOTI", "EDEA", "LOUM",
                "NKONGSAMBA", "OBALA", "EBOLOWA", "AMBAM", "KRIBI", 
                "BERTOUA", "KOUMASSI", "MEINGANGA", "NGAOUNDERE", "GAROUA", 
                "MAROUA", "YAGOUA", "KOUSSERI", "BAFOUSSAM", "DSCHANG", 
                "LIMBE", "OMBE"
            ],
            "ADC": [
                "YAOUNDE", "GAROUA", "DOUALA"
            ],
            # Ajouter d'autres associations client sites ici...
        }

        # Pour chaque client et la liste de ses sites
        for client_name, site_names in associations.items():
            try:
                client = Client.objects.get(name=client_name)
                for site_name in site_names:
                    try:
                        site = Site.objects.get(name=site_name)
                        # Utiliser le modèle intermédiaire pour créer une association
                        client_site, created = ClientSite.objects.get_or_create(client=client, site=site)
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Site {site_name} associé à {client_name}."))
                    except Site.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Site {site_name} n'existe pas."))
            except Client.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Client {client_name} n'existe pas."))
