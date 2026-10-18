from django.contrib import admin
from .models import CategorieGalerie, PhotoGalerie


@admin.register(CategorieGalerie)
class CategorieGalerieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'nombre_photos')
    prepopulated_fields = {'slug': ('nom',)}

    def nombre_photos(self, obj):
        return obj.photos.count()
    nombre_photos.short_description = 'Photos'


@admin.register(PhotoGalerie)
class PhotoGalerieAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'publie', 'date_ajout')
    list_editable = ('publie',)
    list_filter = ('categorie', 'publie', 'date_ajout')
    search_fields = ('titre',)
    date_hierarchy = 'date_ajout'
    actions = ['publier', 'depublier']

    @admin.action(description='✅ Publier')
    def publier(self, request, queryset):
        queryset.update(publie=True)

    @admin.action(description='🚫 Dépublier')
    def depublier(self, request, queryset):
        queryset.update(publie=False)
