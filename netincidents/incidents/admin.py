from django.contrib import admin
from .models import Incident, Equipement, Commentaire, HistoriqueStatut, Notification, ProfilUtilisateur


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['id', 'titre', 'categorie', 'priorite', 'statut', 'cree_par', 'assigne_a', 'date_creation']
    list_filter = ['statut', 'priorite', 'categorie']
    search_fields = ['titre', 'description']
    date_hierarchy = 'date_creation'
    filter_horizontal = ['equipements']
    readonly_fields = ['date_creation', 'date_modification']


@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_equipement', 'adresse_ip', 'localisation', 'statut']
    list_filter = ['type_equipement', 'statut']
    search_fields = ['nom', 'adresse_ip']


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ['incident', 'auteur', 'type_commentaire', 'date_creation']
    list_filter = ['type_commentaire']


@admin.register(HistoriqueStatut)
class HistoriqueAdmin(admin.ModelAdmin):
    list_display = ['incident', 'ancien_statut', 'nouveau_statut', 'modifie_par', 'date_changement']
    readonly_fields = ['date_changement']


@admin.register(ProfilUtilisateur)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'departement', 'telephone']
    list_filter = ['role']


admin.site.register(Notification)

admin.site.site_header = "NetIncidents — Administration"
admin.site.site_title = "NetIncidents"
admin.site.index_title = "Gestion des incidents réseaux"
