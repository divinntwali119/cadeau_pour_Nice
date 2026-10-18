from django.contrib import admin
from .models import Culte, ProgrammeHebdomadaire


class ProgrammeHebdomadaireInline(admin.TabularInline):
    model = ProgrammeHebdomadaire
    extra = 3
    ordering = ('ordre',)


@admin.register(Culte)
class CulteAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_culte', 'get_jour_display', 'heure_debut', 'est_en_direct', 'actif')
    list_editable = ('actif', 'est_en_direct')
    list_filter = ('type_culte', 'jour', 'actif')
    search_fields = ('titre', 'description', 'lieu')
    ordering = ('ordre', 'jour')
    inlines = [ProgrammeHebdomadaireInline]
    actions = ['activer', 'desactiver', 'marquer_en_direct']

    @admin.action(description='✅ Activer les cultes sélectionnés')
    def activer(self, request, queryset):
        queryset.update(actif=True)

    @admin.action(description='❌ Désactiver les cultes sélectionnés')
    def desactiver(self, request, queryset):
        queryset.update(actif=False)

    @admin.action(description='🔴 Marquer EN DIRECT')
    def marquer_en_direct(self, request, queryset):
        Culte.objects.update(est_en_direct=False)
        queryset.update(est_en_direct=True)
        self.message_user(request, "Culte(s) marqué(s) en direct.")
