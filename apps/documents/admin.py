# apps/documents/admin.py

from django.contrib import admin
from apps.documents.models import QRCode, Dossier, Fichier

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'url')
    search_fields = ('numero', 'url')

@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)

@admin.register(Fichier)
class FichierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'dossier', 'date_upload')
    list_filter = ('type', 'date_upload')
    search_fields = ('name',)
    date_hierarchy = 'date_upload'
