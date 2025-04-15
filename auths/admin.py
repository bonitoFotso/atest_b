from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Inspecteur, Formateur
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    # Les champs à afficher dans la liste des utilisateurs
    list_display = ('email', 'full_name', 'is_staff', 'is_active', 'staff_type', 'email_verified')
    list_filter = ('is_staff', 'is_active', 'email_verified')

    # Les champs à utiliser dans le formulaire de l'utilisateur
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {'fields': ('full_name',)}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'email_verified')}),
        (_('groups'), {'fields': ('groups',)}),
    )

    # Les champs lors de la création d'un utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'staff_type')  # Affiche uniquement dans l'admin en mode lecture

    search_fields = ('email', 'full_name')
    ordering = ('email',)
    filter_horizontal = ()


# Enregistrement des profils spécifiques dans l'admin
class InspecteurAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialisation', 'zone_inspection')


class FormateurAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise', 'years_experience')




# Enregistrer les modèles dans l'admin
admin.site.register(User, UserAdmin)
admin.site.register(Inspecteur, InspecteurAdmin)
admin.site.register(Formateur, FormateurAdmin)
