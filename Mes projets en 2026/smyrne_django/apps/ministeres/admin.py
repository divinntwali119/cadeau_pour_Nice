from django.contrib import admin
from .models import Pasteur, Ministere, Departement, Chorale


@admin.register(Pasteur)
class PasteurAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'titre', 'actif')
    list_editable = ('actif',)
    search_fields = ('nom', 'prenom', 'titre')


class DepartementInline(admin.TabularInline):
    model = Departement
    extra = 1
    show_change_link = True


@admin.register(Ministere)
class MinistereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'responsable', 'ordre', 'actif')
    list_editable = ('ordre', 'actif')
    search_fields = ('nom', 'responsable')
    inlines = [DepartementInline]
    ordering = ('ordre',)


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ministere', 'responsable', 'ordre', 'actif')
    list_editable = ('ordre', 'actif')
    list_filter = ('ministere', 'actif')
    search_fields = ('nom', 'responsable')
    ordering = ('ministere', 'ordre')


@admin.register(Chorale)
class ChoraleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'chef_choeur', 'ordre', 'actif')
    list_editable = ('ordre', 'actif')
    search_fields = ('nom', 'chef_choeur')
    ordering = ('ordre',)
