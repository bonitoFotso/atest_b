# apps/geography/admin.py

from django.contrib import admin
from apps.geography.models import Region, City, Site

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'region_name')
    search_fields = ('region_name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city')
    list_filter = ('city',)
    search_fields = ('name',)
