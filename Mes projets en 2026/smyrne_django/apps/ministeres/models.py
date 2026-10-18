"""
=============================================================
MODÈLES — App Ministères
=============================================================
Gère : Pasteur actuel, Ministères, Départements, Chorales.
"""

from django.db import models
from ckeditor.fields import RichTextField


class Pasteur(models.Model):
    """Pasteur actuel ou dirigeant principal de l'église."""

    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    titre = models.CharField(max_length=200, default="Pasteur Principal", verbose_name="Titre")
    biographie = RichTextField(verbose_name="Biographie")
    photo = models.ImageField(upload_to='pasteurs/', blank=True, null=True, verbose_name="Photo")
    facebook = models.URLField(blank=True, verbose_name="Lien Facebook")
    youtube = models.URLField(blank=True, verbose_name="Lien YouTube")
    email = models.EmailField(blank=True, verbose_name="Email")
    actif = models.BooleanField(default=True, verbose_name="Pasteur actuel")

    class Meta:
        verbose_name = "Pasteur"
        verbose_name_plural = "Pasteurs"

    def __str__(self):
        return f"{self.titre} {self.prenom} {self.nom}"

    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class Ministere(models.Model):
    """Ministère de l'église (ex: Jeunesse, Femmes, Évangélisation...)."""

    nom = models.CharField(max_length=200, verbose_name="Nom du ministère")
    description = RichTextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='ministeres/', blank=True, null=True, verbose_name="Image")
    responsable = models.CharField(max_length=200, blank=True, verbose_name="Responsable")
    email_contact = models.EmailField(blank=True, verbose_name="Email de contact")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Ministère"
        verbose_name_plural = "Ministères"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom


class Departement(models.Model):
    """Département rattaché à un ministère."""

    nom = models.CharField(max_length=200, verbose_name="Nom du département")
    description = RichTextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='departements/', blank=True, null=True, verbose_name="Image")
    ministere = models.ForeignKey(
        Ministere, on_delete=models.CASCADE,
        related_name='departements', verbose_name="Ministère parent"
    )
    responsable = models.CharField(max_length=200, blank=True, verbose_name="Responsable")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return f"{self.ministere.nom} › {self.nom}"


class Chorale(models.Model):
    """Chorale ou groupe musical actuel de l'église."""

    nom = models.CharField(max_length=200, verbose_name="Nom de la chorale")
    description = RichTextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='chorales/', blank=True, null=True, verbose_name="Photo")
    chef_choeur = models.CharField(max_length=200, blank=True, verbose_name="Chef de chœur")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    actif = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Chorale"
        verbose_name_plural = "Chorales"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom
