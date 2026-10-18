from django.contrib import admin
from .models import Predication


@admin.register(Predication)
class PredicationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'predicateur', 'publie', 'date_publication')
    list_editable = ('publie',)
    list_filter = ('publie', 'date_publication')
    search_fields = ('titre', 'predicateur', 'description')
    prepopulated_fields = {'slug': ('titre',)}
    date_hierarchy = 'date_publication'
    ordering = ('-date_publication',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'slug', 'predicateur', 'description', 'image')
        }),
        ('Médias', {
            'fields': ('video_fichier', 'video_url', 'audio_fichier'),
            'description': 'Téléchargez un fichier ou collez un lien YouTube/Vimeo.'
        }),
        ('Contenu & Publication', {
            'fields': ('contenu', 'publie', 'date_publication')
        }),
    )
    actions = ['publier', 'depublier']

    @admin.action(description='✅ Publier les prédications sélectionnées')
    def publier(self, request, queryset):
        queryset.update(publie=True)

    @admin.action(description='❌ Dépublier les prédications sélectionnées')
    def depublier(self, request, queryset):
        queryset.update(publie=False)
