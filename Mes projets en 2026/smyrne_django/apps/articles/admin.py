from django.contrib import admin
from django.utils import timezone
from .models import CategorieArticle, Article, Commentaire, Like


@admin.register(CategorieArticle)
class CategorieArticleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'couleur')
    prepopulated_fields = {'slug': ('nom',)}


class CommentaireInline(admin.TabularInline):
    model = Commentaire
    extra = 0
    readonly_fields = ('auteur', 'texte', 'date_creation')
    can_delete = True


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'categorie', 'statut', 'date_publication', 'vues')
    list_editable = ('statut',)
    list_filter = ('statut', 'categorie', 'auteur', 'date_publication')
    search_fields = ('titre', 'resume', 'corps')
    prepopulated_fields = {'slug': ('titre',)}
    date_hierarchy = 'date_publication'
    readonly_fields = ('vues', 'date_creation', 'date_modification')
    inlines = [CommentaireInline]
    actions = ['publier', 'archiver', 'mettre_en_brouillon']

    fieldsets = (
        ('Contenu', {
            'fields': ('titre', 'slug', 'resume', 'corps', 'image', 'video_fichier', 'video_url')
        }),
        ('Classification', {
            'fields': ('auteur', 'categorie')
        }),
        ('Publication', {
            'fields': ('statut', 'date_publication')
        }),
        ('Statistiques', {
            'fields': ('vues', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

    @admin.action(description='✅ Publier maintenant')
    def publier(self, request, queryset):
        queryset.update(statut='publie', date_publication=timezone.now())

    @admin.action(description='📦 Archiver')
    def archiver(self, request, queryset):
        queryset.update(statut='archive')

    @admin.action(description='📝 Remettre en brouillon')
    def mettre_en_brouillon(self, request, queryset):
        queryset.update(statut='brouillon')


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'article', 'approuve', 'date_creation')
    list_editable = ('approuve',)
    list_filter = ('approuve',)
    search_fields = ('auteur__username', 'texte')
    actions = ['approuver', 'desapprouver']

    @admin.action(description='✅ Approuver')
    def approuver(self, request, queryset):
        queryset.update(approuve=True)

    @admin.action(description='❌ Désapprouver')
    def desapprouver(self, request, queryset):
        queryset.update(approuve=False)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'article', 'date_creation')
    list_filter = ('date_creation',)
    readonly_fields = ('utilisateur', 'article', 'date_creation')
