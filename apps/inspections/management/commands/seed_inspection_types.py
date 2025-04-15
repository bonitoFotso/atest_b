from django.core.management.base import BaseCommand

from apps.inspections.models import InspectionType


class Command(BaseCommand):
    help = 'Seed the InspectionType model with predefined types'

    def handle(self, *args, **kwargs):
        inspection_types = [
            {'name': InspectionType.LEVAGE},
            {'name': InspectionType.THERMOGRAPHIQUE},
            {'name': InspectionType.ELECTRIQUE},
            {'name': InspectionType.EXTINCTEUR},
        ]

        for inspection_type_data in inspection_types:
            inspection_type, created = InspectionType.objects.get_or_create(
                name=inspection_type_data['name']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Type d'inspection '{inspection_type.get_name_display()}' créé avec succès."))
            else:
                self.stdout.write(self.style.WARNING(f"Type d'inspection '{inspection_type.get_name_display()}' existe déjà."))
