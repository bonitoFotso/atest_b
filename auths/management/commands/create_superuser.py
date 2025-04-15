import os

from decouple import config
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from auths.models import User


class Command(BaseCommand):
    help = 'Create admin users'

    def handle(self, *args, **kwargs):
        admin_email = config('SUPERUSER_EMAIL')
        admin_password = config('SUPERUSER_PASSWORD')
        full_name = config('SUPERUSER_USERNAME')

        inspecteurs_group, created = Group.objects.get_or_create(name='Inspecteurs')

        # Créer le premier admin
        if not User.objects.filter(email=admin_email).exists():
            superuser = User.objects.create_superuser(
                email=admin_email,
                password=admin_password,
                full_name=full_name
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created admin user {admin_email}'))
            superuser.groups.add(inspecteurs_group)
            self.stdout.write(self.style.SUCCESS(
                f"Inspecteur '{superuser.email}' créé avec succès et ajouté au groupe 'Inspecteurs'."))
        else:
            self.stdout.write(self.style.WARNING(f'Admin user {admin_email} already exists'))

