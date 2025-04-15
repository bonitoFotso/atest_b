from django.contrib import admin
from apps.clients.models import Client, Affaire, Statut, ClientSite
from apps.clients.forms import AffaireAdminForm

@admin.register(Statut)
class StatutAdmin(admin.ModelAdmin):
    list_display = ('id', 'status_name')
    search_fields = ('status_name',)

class ClientSiteInline(admin.TabularInline):
    model = ClientSite
    extra = 1  # Nombre de lignes supplémentaires que vous souhaitez voir


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact', 'email', 'website')
    search_fields = ('name', 'contact', 'email')
    inlines = [ClientSiteInline]  # Utilisez l'inline pour gérer les relations avec les sites

@admin.register(Affaire)
class AffaireAdmin(admin.ModelAdmin):
    form = AffaireAdminForm  # Utilisation du formulaire personnalisé
    list_display = ('id', 'client', 'customer_representative_name', 'status', 'creer_par')
    list_filter = ('status', 'creer_par')
    search_fields = ('customer_representative_name', 'client__name')
    filter_horizontal = ('sites',)
