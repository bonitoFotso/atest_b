from apps.formations.models import HabilitationType, Tension, Role
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Seed the database with HabilitationType, Tension, and Role data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Habilitation Types...")
        self.seed_habilitation_types()

        self.stdout.write("Seeding Tensions...")
        self.seed_tensions()

        self.stdout.write("Seeding Roles...")
        self.seed_roles()

        self.stdout.write(self.style.SUCCESS("Seeding terminé."))

    def seed_habilitation_types(self):
        habilitation_types = [
            {"code": "B0", "description": "Travaux à proximité hors tension BT."},
            {"code": "B1", "description": "Travaux hors tension BT."},
            {"code": "B1V", "description": "Travaux hors tension BT avec consignation."},
            {"code": "B2", "description": "Travaux hors tension BT sous responsabilité."},
            {"code": "B2V", "description": "Travaux hors tension BT avec consignation sous responsabilité."},
            {"code": "BR", "description": "Dépannage ou intervention rapide BT."},
            {"code": "BE Manoeuvre", "description": "Manœuvres BT."},
            {"code": "BE Mesurage", "description": "Mesures électriques BT."},
            {"code": "BE Vérification", "description": "Vérifications d’installation BT."},
            {"code": "H0", "description": "Travaux à proximité hors tension HT."},
            {"code": "H1", "description": "Travaux hors tension HT."},
            {"code": "H1V", "description": "Travaux hors tension HT avec consignation."},
            {"code": "H2", "description": "Travaux hors tension HT sous responsabilité."},
            {"code": "H2V", "description": "Travaux hors tension HT avec consignation sous responsabilité."},
            {"code": "HC", "description": "Consignation en HT."},
            {"code": "T", "description": "Travaux sous tension."},
        ]

        for habilitation in habilitation_types:
            obj, created = HabilitationType.objects.get_or_create(
                code=habilitation["code"],
                defaults={"description": habilitation["description"]},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Ajouté : {obj.code} - {obj.description}"))
            else:
                self.stdout.write(f"Existant : {obj.code} - {obj.description}")

    def seed_tensions(self):
        tensions = [
            {"nom": "BT", "choices": "Basse Tension"},
            {"nom": "HT", "choices": "Haute Tension"},
            {"nom": "HTA", "choices": "Haute Tension A"},
        ]

        for tension in tensions:
            obj, created = Tension.objects.get_or_create(
                nom=tension["nom"]
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Ajouté : {obj.nom} - {tension['choices']}"))
            else:
                self.stdout.write(f"Existant : {obj.nom}")

    def seed_roles(self):
        roles = [
            {"name": "EXECUTANT", "description": "Exécutant"},
            {"name": "CHARGE_TRAVAUX", "description": "Chargé de travaux"},
            {"name": "CHARGE_INTERVENTION_BT", "description": "Chargé d’intervention BT"},
            {"name": "CHARGE_CONSIGNATION", "description": "Chargé de consignation"},
        ]

        for role in roles:
            obj, created = Role.objects.get_or_create(
                name=role["name"]
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Ajouté : {obj.name} - {role['description']}"))
            else:
                self.stdout.write(f"Existant : {obj.name}")
