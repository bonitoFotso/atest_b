# your_app/management/commands/seed.py

import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from apps.clients.models import Affaire, Client, Statut
from apps.documents.models import QRCode
from apps.geography.models import Site, City, Region
from apps.inspections.models import InspectionType

User = get_user_model()

class Command(BaseCommand):
    help = "Seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('Deleting old data...')
        self._clear_data()
        self.stdout.write('Creating new data...')
        self._create_data()
        self.stdout.write('Seeding completed successfully.')

    def _clear_data(self):
        """Efface les données existantes."""
        models = [
            Affaire, Client, Site, City, Region, Statut, InspectionType,
            QRCode, LotEtiquette, Etiquette, Rapport, CertificaType, Session,
            Participant, Certificat, Dossier, Fichier, ArcFlashLabel
        ]
        for model in models:
            model.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

    def _create_data(self):
        """Crée de nouvelles données pour chaque modèle."""
        fake = Faker('fr_FR')
        Faker.seed(0)
        random.seed(0)

        # Créer des utilisateurs
        users = []
        for _ in range(5):
            user = User.objects.create_user(
                full_name=fake.user_name(),
                email=fake.email(),
                password='password123'
            )
            users.append(user)

        # Créer des statuts
        statuts = ['En cours', 'Terminé', 'Annulé']
        status_objects = []
        for statut in statuts:
            status = Statut.objects.create(status_name=statut)
            status_objects.append(status)

        # Régions du Cameroun
        regions_data = [
            'Adamaoua',
            'Centre',
            'Est',
            'Extrême-Nord',
            'Littoral',
            'Nord',
            'Nord-Ouest',
            'Ouest',
            'Sud',
            'Sud-Ouest'
        ]

        # Créer les régions
        regions = []
        for region_name in regions_data:
            region = Region.objects.create(region_name=region_name)
            regions.append(region)

        # Villes par région
        cities_data = {
            'Adamaoua': ['Ngaoundéré', 'Meiganga', 'Tignère'],
            'Centre': ['Yaoundé', 'Mbalmayo', 'Obala'],
            'Est': ['Bertoua', 'Abong-Mbang', 'Batouri'],
            'Extrême-Nord': ['Maroua', 'Kousséri', 'Mokolo'],
            'Littoral': ['Douala', 'Nkongsamba', 'Edéa'],
            'Nord': ['Garoua', 'Guider', 'Poli'],
            'Nord-Ouest': ['Bamenda', 'Kumbo', 'Wum'],
            'Ouest': ['Bafoussam', 'Dschang', 'Foumban'],
            'Sud': ['Ebolowa', 'Kribi', 'Sangmélima'],
            'Sud-Ouest': ['Buea', 'Limbe', 'Kumba'],
        }

        # Créer les villes
        cities = []
        for region_name, city_names in cities_data.items():
            region = Region.objects.get(region_name=region_name)
            for city_name in city_names:
                city = City.objects.create(
                    name=city_name,
                    region=region
                )
                cities.append(city)

        # Créer des sites
        sites = []
        for _ in range(10):
            site = Site.objects.create(
                name=fake.company(),
                city=random.choice(cities)
            )
            sites.append(site)

        # Créer des clients
        clients = []
        for _ in range(5):
            client_sites = random.sample(sites, k=random.randint(1, 3))
            client = Client.objects.create(
                name=fake.company(),
                contact=fake.name(),
                email=fake.company_email(),
                address=fake.address(),
                website=fake.url()
            )
            client.sites.set(client_sites)
            clients.append(client)

        # Créer des affaires
        for _ in range(10):
            client = random.choice(clients)
            affaire_sites = client.sites.all()
            affaire = Affaire.objects.create(
                customer_representative_name=fake.name(),
                customer_representative_function=fake.job(),
                status=random.choice(status_objects),
                creer_par=random.choice(users),
                client=client
            )
            affaire.sites.set(affaire_sites)

        # Créer des types d'inspection
        inspection_types = []
        for name in ['Sécurité', 'Électrique', 'Mécanique']:
            inspection_type = InspectionType.objects.create(name=name)
            inspection_types.append(inspection_type)

        # Créer des QR Codes
        qr_codes = []
        for _ in range(20):
            qr_code = QRCode.objects.create(
                url=fake.url(),
                numero=fake.uuid4()
            )
            qr_codes.append(qr_code)

        # Créer des lots d'étiquettes
        for _ in range(5):
            lot = LotEtiquette.objects.create(
                total=random.randint(10, 50),
                inspectionType=random.choice(inspection_types),
                site=random.choice(sites)
            )


        certificat_types = []
        for name in ['Formation Sécurité', 'Certification ISO']:
            certificat_type = CertificaType.objects.create(name=name)
            certificat_types.append(certificat_type)

        # Créer des sessions
        sessions = []
        for _ in range(5):
            session = Session.objects.create(
                mois=random.choice(Session.MOIS_CHOICES)[0],
                annee=random.randint(2020, timezone.now().year),
                certificaType=random.choice(certificat_types)
            )
            sessions.append(session)

        # Créer des participants
        participants = []
        for _ in range(30):
            participant = Participant.objects.create(
                sexe=random.choice(['M', 'F']),
                nom=fake.last_name(),
                prenom=fake.first_name(),
                date_naissance=fake.date_of_birth(minimum_age=18, maximum_age=65),
                lieu_naissance=fake.city(),
                numero_cni=fake.ssn(),
                entreprise=fake.company(),
                poste=fake.job()
            )
            participant.sessions.set(random.sample(sessions, k=random.randint(1, 3)))
            participants.append(participant)

        # Créer des certificats
        for participant in participants:
            for session in participant.sessions.all():
                Certificat.objects.create(
                    name=f"Certificat {session.certificaType.name}",
                    session=session,
                    participant=participant,
                    qrcode=random.choice(qr_codes),
                    fichier=None  # Ajoutez un fichier si nécessaire
                )

        # Créer des dossiers
        dossiers = []
        for _ in range(5):
            dossier = Dossier.objects.create(
                name=fake.word(),
                description=fake.text()
            )
            dossiers.append(dossier)

        # Créer des fichiers
        for _ in range(10):
            Fichier.objects.create(
                dossier=random.choice(dossiers),
                name=fake.file_name(),
                fichier=None,  # Ajoutez un fichier si nécessaire
                type=random.choice(['Rapport', 'Certificat', 'Etiquette', 'QRCode'])
            )

        # Créer des étiquettes ArcFlash
        for _ in range(10):
            ArcFlashLabel.objects.create(
                site=random.choice(sites),
                cabinet_number=fake.bothify(text='CAB###'),
                repere=fake.word(),
                network_voltage=random.uniform(220.0, 380.0),
                gloves_class=random.choice(['Classe 0', 'Classe 1', 'Classe 2']),
                protection_distance=f"{random.randint(100, 1000)} mm",
                max_energy=f"{random.uniform(1.0, 40.0):.2f} Cal/cm²",
                incident_energy=f"{random.uniform(1.0, 40.0):.2f} Cal/cm²",
                working_distance=f"{random.randint(100, 1000)} mm",
                ppe_category=f"Catégorie {random.randint(1, 4)}",
                ik3max=f"{random.uniform(5.0, 50.0):.2f} kA",
                inspection_date=fake.date_between(start_date='-1y', end_date='today'),
                qrcode=random.choice(qr_codes),
                fichier=None  # Ajoutez un fichier si nécessaire
            )
