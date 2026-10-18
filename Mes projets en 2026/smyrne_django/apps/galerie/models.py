"""
=============================================================
MODÈLES — App Galerie
=============================================================
Gère : Photos et catégories de photos.
"""

from django.db import models


class CategorieGalerie(models.Model):
    """Catégorie de photos (ex: Cultes, Événements, Chorales...)."""

    nom = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True, verbose_name="Slug (URL)")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Catégorie de galerie"
        verbose_name_plural = "Catégories de galerie"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class PhotoGalerie(models.Model):
    """Photo de la galerie du site."""

    titre = models.CharField(max_length=200, blank=True, verbose_name="Titre / Légende")
    image = models.ImageField(upload_to='galerie/', verbose_name="Photo")
    categorie = models.ForeignKey(
        CategorieGalerie, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='photos', verbose_name="Catégorie"
    )
    date_prise = models.DateField(blank=True, null=True, verbose_name="Date de la prise de vue")
    publie = models.BooleanField(default=True, verbose_name="Publié")
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Photo de galerie"
        verbose_name_plural = "Photos de galerie"
        ordering = ['-date_ajout']

    def __str__(self):
        return self.titre or f"Photo #{self.pk}"
