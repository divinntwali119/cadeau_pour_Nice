"""
=============================================================
MODÈLES — App Articles (Actualités)
=============================================================
Gère : Articles, Catégories, Commentaires, Likes.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from ckeditor_uploader.fields import RichTextUploadingField
from apps.core.validators import validate_video_file
from .validators import get_video_embed_url, validate_video_url


class CategorieArticle(models.Model):
    """Catégorie d'articles (ex: Annonce, Événement, Témoignage...)."""

    nom = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True, verbose_name="Slug (URL)")
    couleur = models.CharField(max_length=20, default="#0284c7", verbose_name="Couleur (hex)")

    class Meta:
        verbose_name = "Catégorie d'article"
        verbose_name_plural = "Catégories d'articles"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Article(models.Model):
    """Article / Actualité du site."""

    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('archive', 'Archivé'),
    ]

    titre = models.CharField(max_length=300, verbose_name="Titre")
    slug = models.SlugField(unique=True, max_length=350, verbose_name="Slug (URL)")
    resume = models.TextField(max_length=500, blank=True, verbose_name="Résumé")
    corps = RichTextUploadingField(verbose_name="Contenu complet")
    auteur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='articles', verbose_name="Auteur"
    )
    categorie = models.ForeignKey(
        CategorieArticle, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='articles', verbose_name="Catégorie"
    )
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name="Image principale")
    video_fichier = models.FileField(
        upload_to='articles/videos/',
        blank=True,
        null=True,
        verbose_name="Fichier vidéo (MP4/WebM/MOV)",
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'mov']),
            validate_video_file,
        ],
    )
    video_url = models.URLField(
        blank=True,
        verbose_name="Lien vidéo YouTube/Vimeo",
        help_text="Ajoutez un lien YouTube ou Vimeo. Si un lien et un fichier sont fournis, le lien sera affiché en premier.",
        validators=[validate_video_url],
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon', verbose_name="Statut")
    date_publication = models.DateTimeField(blank=True, null=True, verbose_name="Date de publication")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    vues = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-date_publication', '-date_creation']

    def __str__(self):
        return self.titre

    def nombre_likes(self):
        return self.likes.count()

    def nombre_commentaires(self):
        return self.commentaires.filter(approuve=True).count()

    @property
    def contenu(self):
        return self.corps

    @property
    def chapo(self):
        return self.resume

    @property
    def image_principale(self):
        return self.image

    @property
    def has_video(self):
        return bool(self.video_fichier or self.video_url)

    @property
    def video_embed_url(self):
        return get_video_embed_url(self.video_url)

    @property
    def video_mime_type(self):
        if not self.video_fichier:
            return ''
        extension = self.video_fichier.name.rsplit('.', 1)[-1].lower()
        return {
            'mp4': 'video/mp4',
            'webm': 'video/webm',
            'mov': 'video/quicktime',
        }.get(extension, 'application/octet-stream')


class Commentaire(models.Model):
    """Commentaire d'un utilisateur sur un article."""

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        related_name='commentaires', verbose_name="Article"
    )
    auteur = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='commentaires', verbose_name="Auteur"
    )
    texte = models.TextField(verbose_name="Commentaire")
    approuve = models.BooleanField(default=False, verbose_name="Approuvé")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.auteur.username} — {self.article.titre[:50]}"


class Like(models.Model):
    """Like d'un utilisateur sur un article (un seul par utilisateur)."""

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        related_name='likes', verbose_name="Article"
    )
    utilisateur = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='likes', verbose_name="Utilisateur"
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        unique_together = ('article', 'utilisateur')

    def __str__(self):
        return f"{self.utilisateur.username} ♥ {self.article.titre[:50]}"
