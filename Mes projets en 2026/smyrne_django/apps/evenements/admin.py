from django.contrib import admin
from .models import Evenement, InscriptionEvenement


class InscriptionInline(admin.TabularInline):
    model = InscriptionEvenement
    extra = 0
    readonly_fields = ('nom', 'prenom', 'email', 'telephone', 'date_inscription')
    can_delete = False


@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date_debut', 'lieu', 'inscriptions_ouvertes', 'publie', 'nombre_inscrits')
    list_editable = ('inscriptions_ouvertes', 'publie')
    list_filter = ('publie', 'inscriptions_ouvertes', 'date_debut')
    search_fields = ('titre', 'description', 'lieu')
    prepopulated_fields = {'slug': ('titre',)}
    date_hierarchy = 'date_debut'
    inlines = [InscriptionInline]
    actions = ['ouvrir_inscriptions', 'fermer_inscriptions', 'publier', 'depublier']

    def nombre_inscrits(self, obj):
        return obj.inscriptions.count()
    nombre_inscrits.short_description = 'Inscrits'

    @admin.action(description='✅ Ouvrir les inscriptions')
    def ouvrir_inscriptions(self, request, queryset):
        queryset.update(inscriptions_ouvertes=True)

    @admin.action(description='🔒 Fermer les inscriptions')
    def fermer_inscriptions(self, request, queryset):
        queryset.update(inscriptions_ouvertes=False)

    @admin.action(description='👁 Publier')
    def publier(self, request, queryset):
        queryset.update(publie=True)

    @admin.action(description='🚫 Dépublier')
    def depublier(self, request, queryset):
        queryset.update(publie=False)


@admin.register(InscriptionEvenement)
class InscriptionEvenementAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'email', 'telephone', 'evenement', 'date_inscription')
    list_filter = ('evenement', 'date_inscription')
    search_fields = ('nom', 'prenom', 'email')
    readonly_fields = ('date_inscription',)
