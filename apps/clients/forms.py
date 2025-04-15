from django import forms
from django.core.exceptions import ValidationError
from apps.clients.models import Affaire
from apps.geography.models import Site

class AffaireAdminForm(forms.ModelForm):
    class Meta:
        model = Affaire
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        sites = cleaned_data.get('sites')

        if client and sites:
            # Vérifier que tous les sites associés appartiennent au client
            invalid_sites = sites.exclude(id__in=client.sites.values_list('id', flat=True))
            if invalid_sites.exists():
                site_names = ', '.join(invalid_sites.values_list('name', flat=True))
                raise ValidationError(
                    f"Les sites suivants ne sont pas associés au client {client.name} : {site_names}"
                )
        return cleaned_data
