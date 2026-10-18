"""
=============================================================
MODÈLES — App Histoire
=============================================================
Gère : Histoire de l'église, Pasteurs historiques,
       Chorales historiques, Blocs de biographie.
"""

from django.db import models
from ckeditor.fields import RichTextField


class PasteurHistorique(models.Model):
    """Pasteur ayant dirigé l'église dans le passé."""

    nom = models.CharField(max_length=200, verbose_name="Nom complet")
    periode = models.CharField(max_length=100, verbose_name="Période (ex: 1990 - 2005)")
    description = RichTextField(blank=True, verbose_name="Description / Biographie courte")
    image = models.ImageField(upload_to='histoire/pasteurs/', blank=True, null=True, verbose_name="Photo")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre chronologique")

    class Meta:
        verbose_name = "Pasteur historique"
        verbose_name_plural = "Pasteurs historiques"
        ordering = ['ordre']

    def __str__(self):
        return f"{self.nom} ({self.periode})"


class ChoraleHistorique(models.Model):
    """Chorale qui a existé ou évolué dans l'histoire de l'église."""

    nom = models.CharField(max_length=200, verbose_name="Nom de la chorale")
    periode = models.CharField(max_length=100, verbose_name="Période (ex: 2000 - 2010)")
    description = RichTextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='histoire/chorales/', blank=True, null=True, verbose_name="Photo")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre chronologique")

    class Meta:
        verbose_name = "Chorale historique"
        verbose_name_plural = "Chorales historiques"
        ordering = ['ordre']

    def __str__(self):
        return f"{self.nom} ({self.periode})"


class BlocBiographie(models.Model):
    """Bloc de contenu pour la page de biographie du pasteur actuel."""

    TYPE_CHOICES = [
        ('texte', 'Bloc de texte'),
        ('timeline', 'Événement de timeline'),
        ('citation', 'Citation / Verset'),
        ('image', 'Image avec légende'),
    ]

    type_bloc = models.CharField(max_length=20, choices=TYPE_CHOICES, default='texte', verbose_name="Type de bloc")
    titre = models.CharField(max_length=300, blank=True, verbose_name="Titre")
    contenu = RichTextField(blank=True, verbose_name="Contenu")
    image = models.ImageField(upload_to='biographie/', blank=True, null=True, verbose_name="Image")
    date_evenement = models.CharField(max_length=100, blank=True, verbose_name="Date / Année (pour timeline)")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Bloc de biographie"
        verbose_name_plural = "Blocs de biographie"
        ordering = ['ordre']

    def __str__(self):
        return f"[{self.get_type_bloc_display()}] {self.titre or self.contenu[:50]}"
