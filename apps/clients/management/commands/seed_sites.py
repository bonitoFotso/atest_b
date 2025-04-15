from django.core.management.base import BaseCommand

from apps.geography.models import Region, City, Site


class Command(BaseCommand):
    help = 'Seed sites into the database along with their associated cities and regions'

    def handle(self, *args, **kwargs):
        # Liste des sites avec leurs villes et régions associées
        sites_data = [
            {"name": "YAOUNDE", "city": "Yaoundé", "region": "Centre"},
            {"name": "GAROUA", "city": "Garoua", "region": "Nord"},
            {"name": "DOUALA", "city": "Douala", "region": "Littoral"},
            {"name": "CENTRE DE DISTRIBUTION", "city": "Douala", "region": "Littoral"},
            {"name": "BONANJO", "city": "Douala", "region": "Littoral"},
            {"name": "VILLA DG", "city": "Douala", "region": "Littoral"},
            {"name": "OBALA", "city": "Obala", "region": "Centre"},
            {"name": "EBOLOWA", "city": "Ebolowa", "region": "Sud"},
            {"name": "AMBAM", "city": "Ambam", "region": "Sud"},
            {"name": "BERTOUA", "city": "Bertoua", "region": "Est"},
            {"name": "MEINGANGA", "city": "Meinganga", "region": "Adamaoua"},
            {"name": "NGAOUNDERE", "city": "Ngaoundéré", "region": "Adamaoua"},
            {"name": "GAROUA", "city": "Garoua", "region": "Nord"},
            {"name": "MAROUA", "city": "Maroua", "region": "Extrême-Nord"},
            {"name": "YAGOUA", "city": "Yagoua", "region": "Extrême-Nord"},
            {"name": "KOUSSERI", "city": "Kousseri", "region": "Extrême-Nord"},
            {"name": "BAFOUSSAM", "city": "Bafoussam", "region": "Ouest"},
            {"name": "DSCHANG", "city": "Dschang", "region": "Ouest"},
            {"name": "LIMBE", "city": "Limbe", "region": "Sud-Ouest"},
            {"name": "BONANJO", "city": "Douala", "region": "Littoral"},
            {"name": "VILLA DG", "city": "Douala", "region": "Littoral"},
            {"name": "AKWA", "city": "Douala", "region": "Littoral"},
            {"name": "CC-NDOKOTI", "city": "Douala", "region": "Littoral"},
            {"name": "BONABERI", "city": "Douala", "region": "Littoral"},
            {"name": "CED-NDOKOTI", "city": "Douala", "region": "Littoral"},
            {"name": "EDEA", "city": "Edéa", "region": "Littoral"},
            {"name": "LOUM", "city": "Loum", "region": "Littoral"},
            {"name": "NKONGSAMBA", "city": "Nkongsamba", "region": "Littoral"},
            {"name": "OBALA", "city": "Obala", "region": "Centre"},
            {"name": "EBOLOWA", "city": "Ebolowa", "region": "Sud"},
            {"name": "AMBAM", "city": "Ambam", "region": "Sud"},
            {"name": "KRIBI", "city": "Kribi", "region": "Sud"},
            {"name": "BERTOUA", "city": "Bertoua", "region": "Est"},
            {"name": "KOUMASSI", "city": "Koumassi", "region": "Centre"},
            {"name": "MEINGANGA", "city": "Meinganga", "region": "Adamaoua"},
            {"name": "NGAOUNDERE", "city": "Ngaoundéré", "region": "Adamaoua"},
            {"name": "GAROUA", "city": "Garoua", "region": "Nord"},
            {"name": "MAROUA", "city": "Maroua", "region": "Extrême-Nord"},
            {"name": "YAGOUA", "city": "Yagoua", "region": "Extrême-Nord"},
            {"name": "KOUSSERI", "city": "Kousseri", "region": "Extrême-Nord"},
            {"name": "BAFOUSSAM", "city": "Bafoussam", "region": "Ouest"},
            {"name": "DSCHANG", "city": "Dschang", "region": "Ouest"},
            {"name": "LIMBE", "city": "Limbe", "region": "Sud-Ouest"},
            {"name": "OMBE", "city": "Ombe", "region": "Sud-Ouest"},
            # Ajouter d'autres sites ici...
        ]

        # Parcourir chaque site et ville
        for site_data in sites_data:
            region_name = site_data["region"]
            city_name = site_data["city"]
            site_name = site_data["name"]

            # Vérifier si la région existe, sinon la créer
            region, created = Region.objects.get_or_create(region_name=region_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Région {region_name} créée avec succès."))

            # Vérifier si la ville existe, sinon la créer
            city, created = City.objects.get_or_create(name=city_name, region=region)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Ville {city_name} créée avec succès dans la région {region_name}."))

            # Vérifier si le site existe, sinon le créer
            site, created = Site.objects.get_or_create(name=site_name, city=city)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Site {site_name} créé avec succès dans la ville de {city_name}."))
            else:
                self.stdout.write(self.style.WARNING(f"Site {site_name} existe déjà dans la ville de {city_name}."))
