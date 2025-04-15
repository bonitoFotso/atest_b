# apps/geography/serializers.py

from rest_framework import serializers
from .models import Region, City, Site

# Serializers for Region
class RegionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['region_name']



# Serializers for City
class CityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'region']

class CityListSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()

    class Meta:
        model = City
        fields = ['id', 'name', 'region']

class RegionListSerializer(serializers.ModelSerializer):
    cities = CityListSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'region_name', 'cities']

class RegionDetailSerializer(serializers.ModelSerializer):
    cities = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'region_name', 'cities']

class CityDetailSerializer(serializers.ModelSerializer):
    region = RegionDetailSerializer(read_only=True)
    sites = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'region', 'sites']

# Serializers for Site
class SiteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['name', 'city']

class SiteListSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()

    class Meta:
        model = Site
        fields = ['id', 'name', 'city']

class SiteDetailSerializer(serializers.ModelSerializer):
    city = CityDetailSerializer(read_only=True)

    class Meta:
        model = Site
        fields = ['id', 'name', 'city']
