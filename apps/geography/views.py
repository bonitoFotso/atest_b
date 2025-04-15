# apps/geography/views.py

from rest_framework import viewsets
from .models import Region, City, Site
from .serializers import (
    RegionCreateSerializer, RegionListSerializer, RegionDetailSerializer,
    CityCreateSerializer, CityListSerializer, CityDetailSerializer,
    SiteCreateSerializer, SiteListSerializer, SiteDetailSerializer
)

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return RegionListSerializer
        elif self.action == 'retrieve':
            return RegionDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RegionCreateSerializer
        return RegionDetailSerializer

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CityListSerializer
        elif self.action == 'retrieve':
            return CityDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CityCreateSerializer
        return CityDetailSerializer

class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SiteListSerializer
        elif self.action == 'retrieve':
            return SiteDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SiteCreateSerializer
        return SiteDetailSerializer
