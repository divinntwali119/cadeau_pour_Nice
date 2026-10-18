from django.contrib import admin
from .models import DemandePriere, TemoignagePriere


@admin.register(DemandePriere)
class DemandePriereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'sujet', 'confidentiel', 'traite', 'date_creation')
    list_editable = ('traite',)
    list_filter = ('confidentiel', 'traite', 'date_creation')
    search_fields = ('nom', 'sujet', 'message')
    readonly_fields = ('date_creation',)
    date_hierarchy = 'date_creation'
    actions = ['marquer_traite', 'marquer_non_traite']

    @admin.action(description='✅ Marquer comme traité')
    def marquer_traite(self, request, queryset):
        queryset.update(traite=True)

    @admin.action(description='🔄 Marquer comme non traité')
    def marquer_non_traite(self, request, queryset):
        queryset.update(traite=False)


@admin.register(TemoignagePriere)
class TemoignagePriereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'approuve', 'date_creation')
    list_editable = ('approuve',)
    list_filter = ('approuve',)
    search_fields = ('nom', 'texte')
    actions = ['approuver', 'desapprouver']

    @admin.action(description='✅ Approuver')
    def approuver(self, request, queryset):
        queryset.update(approuve=True)

    @admin.action(description='❌ Désapprouver')
    def desapprouver(self, request, queryset):
        queryset.update(approuve=False)
