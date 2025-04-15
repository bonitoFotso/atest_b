# apps/inspections/admin.py

from django.contrib import admin
from apps.inspections.models import (
    InspectionType, LotEtiquette, Etiquette, Rapport, ArcFlashLabel
)

@admin.register(InspectionType)
class InspectionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(LotEtiquette)
class LotEtiquetteAdmin(admin.ModelAdmin):
    list_display = ('id', 'total', 'inspectionType', 'site', 'date_creation')
    list_filter = ('inspectionType', 'site', 'date_creation')
    search_fields = ('site__name',)

@admin.register(Etiquette)
class EtiquetteAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'site', 'inspectionType', 'isAssigned')
    list_filter = ('inspectionType', 'site', 'isAssigned')
    search_fields = ('numero',)
    autocomplete_fields = ('qrcode',)

@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_rapport', 'site', 'inspectionType', 'date_inspection')
    list_filter = ('inspectionType', 'date_inspection')
    search_fields = ('numero_rapport',)
    date_hierarchy = 'date_inspection'
    autocomplete_fields = ('etiquette', 'qrcode', 'business', 'dossier')

@admin.register(ArcFlashLabel)
class ArcFlashLabelAdmin(admin.ModelAdmin):
    list_display = ('id', 'cabinet_number', 'repere', 'site', 'inspection_date')
    list_filter = ('site', 'inspection_date')
    search_fields = ('cabinet_number', 'repere')
    autocomplete_fields = ('qrcode', 'dossier')
