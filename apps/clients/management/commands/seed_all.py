from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Execute all seed commands for the app'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Exécution de seed_clients...'))
        call_command('seed_clients')

        self.stdout.write(self.style.SUCCESS('Exécution de seed_sites...'))
        call_command('seed_sites')

        self.stdout.write(self.style.SUCCESS('Exécution de seed_client_sites...'))
        call_command('seed_client_sites')

        self.stdout.write(self.style.SUCCESS('Exécution de seed_inspection_types...'))
        call_command('seed_inspection_types')

        self.stdout.write(self.style.SUCCESS('Exécution de create_superuser...'))
        call_command('create_superuser')

        self.stdout.write(self.style.SUCCESS('Exécution de seed...'))
        call_command('seed')

        self.stdout.write(self.style.SUCCESS('Toutes les commandes de seed ont été exécutées avec succès.'))

