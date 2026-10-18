"""
=============================================================
MODÈLES — App Événements
=============================================================
Gère : Événements et inscriptions.
"""

from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone


class Evenement(models.Model):
    """Événement de l'église (concert, conférence, retraite, etc.)."""

    titre = models.CharField(max_length=300, verbose_name="Titre")
    slug = models.SlugField(unique=True, max_length=350, verbose_name="Slug (URL)")
    description = RichTextField(verbose_name="Description")
    date_debut = models.DateTimeField(verbose_name="Date et heure de début")
    date_fin = models.DateTimeField(blank=True, null=True, verbose_name="Date et heure de fin")
    lieu = models.CharField(max_length=300, verbose_name="Lieu")
    image = models.ImageField(upload_to='evenements/', blank=True, null=True, verbose_name="Affiche / Image")
    places_max = models.PositiveIntegerField(blank=True, null=True, verbose_name="Nombre de places max (vide = illimité)")
    inscriptions_ouvertes = models.BooleanField(default=True, verbose_name="Inscriptions ouvertes")
    publie = models.BooleanField(default=True, verbose_name="Publié")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['date_debut']

    def __str__(self):
        return self.titre

    def est_passe(self):
        """Retourne True si l'événement est terminé."""
        return self.date_debut < timezone.now()

    def places_restantes(self):
        """Retourne le nombre de places restantes."""
        if self.places_max is None:
            return None
        inscrits = self.inscriptions.count()
        return max(0, self.places_max - inscrits)

    @property
    def description_courte(self):
        return self.description

    @property
    def description_complete(self):
        return self.description


class InscriptionEvenement(models.Model):
    """Inscription d'une personne à un événement."""

    evenement = models.ForeignKey(
        Evenement, on_delete=models.CASCADE,
        related_name='inscriptions', verbose_name="Événement"
    )
    nom = models.CharField(max_length=150, verbose_name="Nom")
    prenom = models.CharField(max_length=150, verbose_name="Prénom")
    email = models.EmailField(verbose_name="Email")
    telephone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    message = models.TextField(blank=True, verbose_name="Message / Remarque")
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Inscription à un événement"
        verbose_name_plural = "Inscriptions aux événements"
        ordering = ['-date_inscription']
        unique_together = ('evenement', 'email')

    def __str__(self):
        return f"{self.prenom} {self.nom} → {self.evenement.titre}"
