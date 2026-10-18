"""
=============================================================
MODÈLES — App Accounts (Authentification & Profils)
=============================================================
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class ProfilMembre(models.Model):
    """Profil étendu d'un membre / utilisateur du site."""

    ROLE_CHOICES = [
        ('membre', 'Membre'),
        ('editeur', 'Éditeur'),
        ('admin', 'Administrateur'),
    ]

    utilisateur = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profil', verbose_name="Utilisateur"
    )
    telephone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    photo = models.ImageField(upload_to='membres/', blank=True, null=True, verbose_name="Photo de profil")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='membre', verbose_name="Rôle")
    bio = models.TextField(blank=True, verbose_name="Bio courte")
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil membre"
        verbose_name_plural = "Profils membres"

    def __str__(self):
        return f"Profil de {self.utilisateur.get_full_name() or self.utilisateur.username}"


# ─── Signal : créer automatiquement un profil quand un User est créé ───
@receiver(post_save, sender=User)
def creer_profil_membre(sender, instance, created, **kwargs):
    """Crée automatiquement un ProfilMembre lors de la création d'un User."""
    if created:
        ProfilMembre.objects.get_or_create(utilisateur=instance)
