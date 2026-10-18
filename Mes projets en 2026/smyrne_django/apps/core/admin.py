"""
=============================================================
ADMIN — App Core
=============================================================
Interface d'administration personnalisée pour le contenu général.
"""

from django.contrib import admin
from .models import (
    SlideCarousel, Temoignage, StatSite, PageContenu, ParametreSite, MoyenDon,
    HomeFeedLike, HomeFeedComment,
)


@admin.register(SlideCarousel)
class SlideCarouselAdmin(admin.ModelAdmin):
    list_display = ('titre', 'ordre', 'actif')
    list_editable = ('ordre', 'actif')
    list_filter = ('actif',)
    search_fields = ('titre', 'sous_titre')
    ordering = ('ordre',)


@admin.register(Temoignage)
class TemoignageAdmin(admin.ModelAdmin):
    list_display = ('nom_auteur', 'role', 'approuve', 'date_creation')
    list_editable = ('approuve',)
    list_filter = ('approuve',)
    search_fields = ('nom_auteur', 'texte')
    actions = ['approuver', 'desapprouver']
    date_hierarchy = 'date_creation'

    @admin.action(description='✅ Approuver les témoignages sélectionnés')
    def approuver(self, request, queryset):
        queryset.update(approuve=True)
        self.message_user(request, f"{queryset.count()} témoignage(s) approuvé(s).")

    @admin.action(description='❌ Désapprouver les témoignages sélectionnés')
    def desapprouver(self, request, queryset):
        queryset.update(approuve=False)
        self.message_user(request, f"{queryset.count()} témoignage(s) désapprouvé(s).")


@admin.register(StatSite)
class StatSiteAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'valeur', 'icone', 'ordre', 'actif')
    list_editable = ('ordre', 'actif', 'valeur')
    ordering = ('ordre',)


@admin.register(PageContenu)
class PageContenuAdmin(admin.ModelAdmin):
    list_display = ('titre', 'slug', 'publie', 'date_modification')
    list_editable = ('publie',)
    search_fields = ('titre', 'slug')
    prepopulated_fields = {'slug': ('titre',)}


@admin.register(ParametreSite)
class ParametreSiteAdmin(admin.ModelAdmin):
    """Paramètres généraux du site — singleton."""
    fieldsets = (
        ('Identité de l\'église', {
            'fields': ('nom_eglise', 'slogan', 'logo')
        }),
        ('Coordonnées', {
            'fields': ('adresse', 'telephone', 'email', 'whatsapp')
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook', 'youtube')
        }),
        ('Culte en Direct', {
            'fields': ('en_direct_actif', 'en_direct_titre', 'en_direct_url'),
            'description': 'Activez cette option le dimanche ou pendant les cultes pour afficher la bannière "EN DIRECT" sur tout le site.'
        }),
    )

    def has_add_permission(self, request):
        """Interdire d'ajouter un 2ème enregistrement."""
        return not ParametreSite.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Interdire la suppression des paramètres."""
        return False


@admin.register(MoyenDon)
class MoyenDonAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'type_moyen', 'numero_compte', 'intitule_compte', 'devise',
        'coordonnees_verifiees', 'ordre', 'actif',
    )
    list_editable = ('coordonnees_verifiees', 'ordre', 'actif')
    list_filter = ('type_moyen', 'coordonnees_verifiees', 'actif')
    search_fields = ('nom', 'numero_compte', 'intitule_compte')
    ordering = ('ordre', 'nom')


@admin.register(HomeFeedLike)
class HomeFeedLikeAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'content_type', 'object_id', 'date_creation')
    list_filter = ('content_type', 'date_creation')
    search_fields = ('utilisateur__username',)
    readonly_fields = ('date_creation',)


@admin.register(HomeFeedComment)
class HomeFeedCommentAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'content_type', 'object_id', 'approuve', 'date_creation')
    list_editable = ('approuve',)
    list_filter = ('approuve', 'content_type', 'date_creation')
    search_fields = ('auteur__username', 'texte')
    actions = ('approuver_commentaires', 'desapprouver_commentaires')
    date_hierarchy = 'date_creation'

    @admin.action(description='✅ Approuver les commentaires sélectionnés')
    def approuver_commentaires(self, request, queryset):
        queryset.update(approuve=True)

    @admin.action(description='❌ Désapprouver les commentaires sélectionnés')
    def desapprouver_commentaires(self, request, queryset):
        queryset.update(approuve=False)

