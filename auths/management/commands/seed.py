from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from auths.models import User, Inspecteur, Formateur
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
from decouple import config


class Command(BaseCommand):
    help = 'Seed the database with users, inspecteurs, formateurs, participants, and assign groups with permissions'

    def handle(self, *args, **kwargs):
        admin_email = config('SUPERUSER_EMAIL')
        admin_password = config('SUPERUSER_PASSWORD')
        full_name = config('SUPERUSER_USERNAME')

        # Créez des groupes
        self.stdout.write(self.style.SUCCESS("Création des groupes..."))
        inspecteurs_group, created = Group.objects.get_or_create(name='Inspecteurs')
        formateurs_group, created = Group.objects.get_or_create(name='Formateurs')
        participants_group, created = Group.objects.get_or_create(name='Participants')

        self.stdout.write(self.style.SUCCESS("Groupes créés avec succès."))

        # Ajouter des permissions spécifiques aux groupes
        self.stdout.write(self.style.SUCCESS("Ajout des permissions aux groupes..."))
        content_type = ContentType.objects.get_for_model(User)

        # Exemple : Ajout des permissions "add_user", "change_user", etc. aux groupes
        add_user_permission = Permission.objects.get(codename='add_user', content_type=content_type)
        change_user_permission = Permission.objects.get(codename='change_user', content_type=content_type)

        # Ajoutez des permissions au groupe "Inspecteurs"
        inspecteurs_group.permissions.add(add_user_permission, change_user_permission)

        # Vous pouvez personnaliser les permissions pour chaque groupe
        formateurs_group.permissions.add(change_user_permission)
        participants_group.permissions.add(add_user_permission)

        self.stdout.write(self.style.SUCCESS("Permissions ajoutées aux groupes avec succès."))

        # Créez un inspecteur et assignez-le au groupe "Inspecteurs"
        self.stdout.write(self.style.SUCCESS("Création d'un inspecteur..."))
        try:
            inspecteur_user, created = User.objects.get_or_create(
                email='inspecteur@example.com',
                defaults={
                    'full_name': 'Inspecteur User',
                    'password': 'inspecteurpassword123',
                    'is_staff': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Inspecteur '{inspecteur_user.email}' créé avec succès."))
            else:
                self.stdout.write(self.style.WARNING(f"Inspecteur '{inspecteur_user.email}' existe déjà."))
        except IntegrityError:
            self.stdout.write(self.style.ERROR(f"Erreur d'intégrité pour l'email 'inspecteur@example.com'."))

        Inspecteur.objects.get_or_create(
            user=inspecteur_user,
            specialisation='Inspection Levage',
            zone_inspection='Douala'
        )
        inspecteur_user.groups.add(inspecteurs_group)
        self.stdout.write(self.style.SUCCESS(f"Inspecteur '{inspecteur_user.email}' ajouté au groupe 'Inspecteurs'."))

        # Créez un formateur et assignez-le au groupe "Formateurs"
        self.stdout.write(self.style.SUCCESS("Création d'un formateur..."))
        try:
            formateur_user, created = User.objects.get_or_create(
                email='formateur@example.com',
                defaults={
                    'full_name': 'Formateur User',
                    'password': 'formateurpassword123',
                    'is_staff': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Formateur '{formateur_user.email}' créé avec succès."))
            else:
                self.stdout.write(self.style.WARNING(f"Formateur '{formateur_user.email}' existe déjà."))
        except IntegrityError:
            self.stdout.write(self.style.ERROR(f"Erreur d'intégrité pour l'email 'formateur@example.com'."))

        Formateur.objects.get_or_create(
            user=formateur_user,
            expertise='Formateur en sécurité électrique',
            years_experience=10
        )
        formateur_user.groups.add(formateurs_group)
        self.stdout.write(self.style.SUCCESS(f"Formateur '{formateur_user.email}' ajouté au groupe 'Formateurs'."))

        # Créez un participant et assignez-le au groupe "Participants"
