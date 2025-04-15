# apps/certifications/admin.py

from django.contrib import admin
from apps.certifications.models import CertificaType, Session

@admin.register(CertificaType)
class CertificaTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'mois', 'annee', 'certificaType')
    list_filter = ('mois', 'annee', 'certificaType')
    search_fields = ('mois', 'annee', 'certificaType__name')


#@admin.register(Certificat)
#class CertificatAdmin(admin.ModelAdmin):
#    list_display = ('id', 'name', 'participant', 'session')
#    list_filter = ('session',)
#    search_fields = ('name', 'participant__nom', 'participant__prenom')
#    autocomplete_fields = ('participant', 'qrcode', 'dossier')
