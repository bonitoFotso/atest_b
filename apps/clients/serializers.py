from rest_framework import serializers
from .models import Client, Affaire, Statut
from apps.geography.serializers import SiteDetailSerializer

# Serializer pour le modèle Statut (pas de changement nécessaire)
class StatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statut
        fields = '__all__'

# Serializers pour le modèle Client
class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['logo', 'name', 'contact', 'email', 'address', 'website']

class ClientListSerializer(serializers.ModelSerializer):
    sites = SiteDetailSerializer(many=True, read_only=True)
    class Meta:
        model = Client
        fields = ['id', 'logo', 'name', 'contact', 'email', 'address', 'website', 'sites']

class ClientDetailSerializer(serializers.ModelSerializer):
    sites = SiteDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'logo', 'name', 'contact', 'email', 'address', 'website', 'sites']

# Serializers pour le modèle Affaire
from rest_framework import serializers
from .models import Affaire

class AffaireCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affaire
        fields = [
            'customer_representative_name',
            'customer_representative_function',
            'status',
            'creer_par',
            'client',
            'sites'
        ]

    def validate(self, data):
        client = data.get('client')
        sites = data.get('sites')

        if client and sites:
            invalid_sites = sites.exclude(id__in=client.sites.values_list('id', flat=True))
            if invalid_sites.exists():
                site_names = ', '.join(invalid_sites.values_list('name', flat=True))
                raise serializers.ValidationError(
                    f"Les sites suivants ne sont pas associés au client {client.name} : {site_names}"
                )
        return data

class AffaireListSerializer(serializers.ModelSerializer):
    client = ClientListSerializer(read_only=True)
    status = StatutSerializer(read_only=True)

    class Meta:
        model = Affaire
        fields = ['id', 'client', 'status', 'customer_representative_name']

class AffaireDetailSerializer(serializers.ModelSerializer):
    client = ClientDetailSerializer(read_only=True)
    status = StatutSerializer(read_only=True)
    sites = SiteDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Affaire
        fields = '__all__'
