"""
=============================================================
MODÈLES — App Prédications
=============================================================
Gère : Prédications (vidéo, audio, texte).
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from ckeditor.fields import RichTextField
from apps.core.validators import validate_image_file, validate_video_file, validate_audio_file


class Predication(models.Model):
    """Prédication : peut contenir un fichier vidéo, audio ou un lien YouTube."""

    titre = models.CharField(max_length=300, verbose_name="Titre de la prédication")
    slug = models.SlugField(unique=True, max_length=350, verbose_name="Slug (URL)")
    predicateur = models.CharField(max_length=200, verbose_name="Prédicateur")
    description = models.TextField(blank=True, verbose_name="Description courte")
    contenu = RichTextField(blank=True, verbose_name="Contenu complet (transcription)")
    image = models.ImageField(
        upload_to='predications/images/',
        blank=True,
        null=True,
        verbose_name="Image de couverture",
        validators=[validate_image_file]
    )

    # Médias
    video_fichier = models.FileField(
        upload_to='predications/videos/',
        blank=True,
        null=True,
        verbose_name="Fichier vidéo (MP4)",
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'mov']), validate_video_file]
    )
    video_url = models.URLField(blank=True, verbose_name="Lien vidéo YouTube/Vimeo")
    audio_fichier = models.FileField(
        upload_to='predications/audio/',
        blank=True,
        null=True,
        verbose_name="Fichier audio (MP3)",
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a']), validate_audio_file]
    )

    # Publication
    publie = models.BooleanField(default=False, verbose_name="Publié")
    date_publication = models.DateField(blank=True, null=True, verbose_name="Date de prédication")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Prédication"
        verbose_name_plural = "Prédications"
        ordering = ['-date_publication', '-date_creation']

    def __str__(self):
        return self.titre

    def get_embed_url(self):
        """Convertit une URL YouTube en URL embed pour l'intégration iframe."""
        if 'youtube.com/watch?v=' in self.video_url:
            video_id = self.video_url.split('v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        if 'youtu.be/' in self.video_url:
            video_id = self.video_url.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.video_url
