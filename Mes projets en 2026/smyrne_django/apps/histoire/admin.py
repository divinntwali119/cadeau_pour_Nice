from django.contrib import admin
from .models import PasteurHistorique, ChoraleHistorique, BlocBiographie


@admin.register(PasteurHistorique)
class PasteurHistoriqueAdmin(admin.ModelAdmin):
    list_display = ('nom', 'periode', 'ordre')
    list_editable = ('ordre',)
    search_fields = ('nom', 'periode')
    ordering = ('ordre',)


@admin.register(ChoraleHistorique)
class ChoraleHistoriqueAdmin(admin.ModelAdmin):
    list_display = ('nom', 'periode', 'ordre')
    list_editable = ('ordre',)
    search_fields = ('nom', 'periode')
    ordering = ('ordre',)


@admin.register(BlocBiographie)
class BlocBiographieAdmin(admin.ModelAdmin):
    list_display = ('type_bloc', 'titre', 'date_evenement', 'ordre')
    list_editable = ('ordre',)
    list_filter = ('type_bloc',)
    search_fields = ('titre', 'contenu')
    ordering = ('ordre',)
