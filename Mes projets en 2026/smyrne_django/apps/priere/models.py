"""
=============================================================
MODÈLES — App Prière
=============================================================
Gère : Demandes de prière et témoignages de prière.
"""

from django.db import models


class DemandePriere(models.Model):
    """Demande de prière soumise par un visiteur du site."""

    nom = models.CharField(max_length=150, verbose_name="Votre nom")
    email = models.EmailField(blank=True, verbose_name="Email (optionnel)")
    sujet = models.CharField(max_length=300, verbose_name="Sujet de la prière")
    message = models.TextField(verbose_name="Description de votre besoin")
    confidentiel = models.BooleanField(default=False, verbose_name="Confidentiel (visible par l'équipe seulement)")
    traite = models.BooleanField(default=False, verbose_name="Traité par l'équipe")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Demande de prière"
        verbose_name_plural = "Demandes de prière"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom} — {self.sujet}"


class TemoignagePriere(models.Model):
    """Témoignage de réponse à une prière (partagé publiquement)."""

    nom = models.CharField(max_length=150, verbose_name="Votre nom")
    texte = models.TextField(verbose_name="Votre témoignage")
    approuve = models.BooleanField(default=False, verbose_name="Approuvé pour publication")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Témoignage de prière"
        verbose_name_plural = "Témoignages de prière"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom} — {self.texte[:60]}..."
