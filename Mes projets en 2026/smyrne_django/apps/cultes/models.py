"""
=============================================================
MODÈLES — App Cultes
=============================================================
Gère : Cultes hebdomadaires et programmes.
"""

from django.db import models


class Culte(models.Model):
    """Culte hebdomadaire ou événement cultuel de l'église."""

    TYPE_CHOICES = [
        ('dominical', 'Culte Dominical'),
        ('semaine', 'Culte de Semaine'),
        ('jeune', 'Culte de Jeûne'),
        ('priere', 'Culte de Prière'),
        ('jeunesse', 'Culte de Jeunesse'),
        ('louange', 'Culte de Louange'),
        ('special', 'Culte Spécial'),
    ]

    JOUR_CHOICES = [
        (0, 'Lundi'), (1, 'Mardi'), (2, 'Mercredi'),
        (3, 'Jeudi'), (4, 'Vendredi'), (5, 'Samedi'), (6, 'Dimanche'),
    ]

    titre = models.CharField(max_length=200, verbose_name="Titre du culte")
    type_culte = models.CharField(max_length=20, choices=TYPE_CHOICES, default='dominical', verbose_name="Type")
    jour = models.IntegerField(choices=JOUR_CHOICES, verbose_name="Jour de la semaine")
    heure_debut = models.TimeField(verbose_name="Heure de début")
    heure_fin = models.TimeField(blank=True, null=True, verbose_name="Heure de fin")
    lieu = models.CharField(max_length=200, default="Sanctuaire CELPA SMYRNE", verbose_name="Lieu")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='cultes/', blank=True, null=True, verbose_name="Image")
    en_direct_url = models.URLField(blank=True, verbose_name="Lien En Direct (YouTube/Facebook)")
    est_en_direct = models.BooleanField(default=False, verbose_name="En direct maintenant")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Culte"
        verbose_name_plural = "Cultes"
        ordering = ['ordre', 'jour', 'heure_debut']

    def __str__(self):
        return f"{self.titre} ({self.get_jour_display()})"

    def get_heure_display(self):
        """Retourne l'heure formatée en français."""
        heure = self.heure_debut.strftime('%Hh%M')
        if self.heure_fin:
            heure += f" — {self.heure_fin.strftime('%Hh%M')}"
        return heure


class ProgrammeHebdomadaire(models.Model):
    """Programme détaillé d'un culte (activités à l'intérieur du culte)."""

    culte = models.ForeignKey(
        Culte, on_delete=models.CASCADE,
        related_name='programmes', verbose_name="Culte associé"
    )
    heure = models.TimeField(verbose_name="Heure")
    activite = models.CharField(max_length=200, verbose_name="Activité")
    responsable = models.CharField(max_length=150, blank=True, verbose_name="Responsable")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Programme hebdomadaire"
        verbose_name_plural = "Programmes hebdomadaires"
        ordering = ['ordre', 'heure']

    def __str__(self):
        return f"{self.culte} — {self.heure.strftime('%Hh%M')} {self.activite}"
