"""
=============================================================
MODÈLES — App Core (Contenu général du site)
=============================================================
Gère : Slides du carousel, Témoignages, Statistiques,
       Pages de contenu, Paramètres du site.
"""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.templatetags.static import static
from ckeditor.fields import RichTextField


class SlideCarousel(models.Model):
    """Slide du carousel de la page d'accueil."""

    titre = models.CharField(max_length=200, verbose_name="Titre")
    sous_titre = models.CharField(max_length=300, blank=True, verbose_name="Sous-titre")
    image = models.ImageField(upload_to='slides/', verbose_name="Image de fond")
    bouton_texte = models.CharField(max_length=100, blank=True, verbose_name="Texte du bouton")
    bouton_lien = models.CharField(max_length=200, blank=True, verbose_name="Lien du bouton")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Slide du carousel"
        verbose_name_plural = "Slides du carousel"
        ordering = ['ordre']

    def __str__(self):
        return self.titre


class Temoignage(models.Model):
    """Témoignage d'un fidèle affiché sur la page d'accueil."""

    nom_auteur = models.CharField(max_length=150, verbose_name="Nom de l'auteur")
    role = models.CharField(max_length=100, blank=True, verbose_name="Rôle / Titre")
    texte = models.TextField(verbose_name="Témoignage")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Photo")
    approuve = models.BooleanField(default=False, verbose_name="Approuvé")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom_auteur} — {self.texte[:50]}..."


class StatSite(models.Model):
    """Statistique affichée sur la page d'accueil (ex: 500 fidèles, 10 ans, etc.)."""

    libelle = models.CharField(max_length=100, verbose_name="Libellé")
    valeur = models.CharField(max_length=50, verbose_name="Valeur (ex: 500+)")
    icone = models.CharField(max_length=100, blank=True, verbose_name="Icône FontAwesome (ex: fa-users)")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Statistique du site"
        verbose_name_plural = "Statistiques du site"
        ordering = ['ordre']

    def __str__(self):
        return f"{self.valeur} {self.libelle}"


class PageContenu(models.Model):
    """Page de contenu générique modifiable depuis l'admin."""

    slug = models.SlugField(unique=True, verbose_name="Slug (URL)")
    titre = models.CharField(max_length=200, verbose_name="Titre")
    contenu = RichTextField(verbose_name="Contenu")
    publie = models.BooleanField(default=True, verbose_name="Publié")
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page de contenu"
        verbose_name_plural = "Pages de contenu"
        ordering = ['titre']

    def __str__(self):
        return self.titre


class ParametreSite(models.Model):
    """Paramètres généraux du site (singleton — un seul enregistrement)."""

    nom_eglise = models.CharField(max_length=200, default="5e CELPA SMYRNE", verbose_name="Nom de l'église")
    slogan = models.CharField(max_length=300, blank=True, verbose_name="Slogan")
    logo = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Logo")
    adresse = models.CharField(max_length=300, blank=True, verbose_name="Adresse")
    telephone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    facebook = models.URLField(blank=True, verbose_name="Lien Facebook")
    youtube = models.URLField(blank=True, verbose_name="Lien YouTube")
    whatsapp = models.CharField(max_length=50, blank=True, verbose_name="Numéro WhatsApp")
    # Culte en direct
    en_direct_actif = models.BooleanField(default=False, verbose_name="Culte en direct actif")
    en_direct_titre = models.CharField(max_length=200, blank=True, default="Culte en direct", verbose_name="Titre du direct")
    en_direct_url = models.URLField(blank=True, verbose_name="Lien vidéo du direct (YouTube / Facebook)")

    class Meta:
        verbose_name = "Paramètre du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return self.nom_eglise

    def get_embed_en_direct_url(self):
        """Convertit l'URL du direct en embed YouTube/Facebook si possible."""
        url = self.en_direct_url or ""
        if 'youtube.com/watch?v=' in url:
            video_id = url.split('v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}?autoplay=1"
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}?autoplay=1"
        if 'youtube.com/live/' in url:
            video_id = url.split('live/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}?autoplay=1"
        return url

    def save(self, *args, **kwargs):
        """S'assurer qu'il n'y a qu'un seul enregistrement de paramètres."""
        self.pk = 1
        super().save(*args, **kwargs)


class MoyenDon(models.Model):
    """Moyen de paiement ou compte pour les dîmes, offrandes et dons."""
    TYPE_CHOICES = [
        ('mobile_money', 'Mobile Money (M-Pesa, Airtel, Orange)'),
        ('banque', 'Compte Bancaire'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100, verbose_name="Nom de la méthode (ex: M-Pesa, Rawbank)")
    type_moyen = models.CharField(max_length=30, choices=TYPE_CHOICES, default='mobile_money', verbose_name="Type")
    numero_compte = models.CharField(max_length=100, verbose_name="Numéro de téléphone ou compte")
    intitule_compte = models.CharField(max_length=150, verbose_name="Bénéficiaire / Titulaire")
    devise = models.CharField(max_length=50, default="USD & CDF", verbose_name="Devise acceptée")
    instructions = models.TextField(blank=True, verbose_name="Instructions pour le donateur")
    logo = models.ImageField(upload_to='moyens_dons/', blank=True, null=True, verbose_name="Logo personnalisé")
    coordonnees_verifiees = models.BooleanField(
        default=False,
        verbose_name="Coordonnées vérifiées",
        help_text="N'afficher ce moyen de paiement qu'après confirmation du numéro ou compte par l'église.",
    )
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Moyen de don"
        verbose_name_plural = "Moyens de dons"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return f"{self.nom} — {self.numero_compte}"

    def save(self, *args, **kwargs):
        """Révoque la validation lorsqu'une coordonnée bancaire est modifiée."""
        if self.pk and self.coordonnees_verifiees:
            ancienne_version = type(self).objects.filter(pk=self.pk).values(
                'nom', 'type_moyen', 'numero_compte', 'intitule_compte',
            ).first()
            champs_a_verifier = ('nom', 'type_moyen', 'numero_compte', 'intitule_compte')
            if ancienne_version and any(
                ancienne_version[champ] != getattr(self, champ)
                for champ in champs_a_verifier
            ):
                self.coordonnees_verifiees = False
                update_fields = kwargs.get('update_fields')
                if update_fields is not None:
                    kwargs['update_fields'] = set(update_fields) | {'coordonnees_verifiees'}
        super().save(*args, **kwargs)

    def get_logo_url(self):
        """Retourne un logo officiel local ou le logo personnalisé téléversé."""
        if self.logo:
            return self.logo.url
        nom_l = self.nom.lower()
        if 'm-pesa' in nom_l or 'mpesa' in nom_l or 'vodacom' in nom_l:
            return static('images/paiements/vodacom.svg')
        if 'airtel' in nom_l:
            return static('images/paiements/airtel.png')
        if 'orange' in nom_l:
            return static('images/paiements/orange-money.svg')
        if 'rawbank' in nom_l:
            return static('images/paiements/rawbank.png')
        if 'tmb' in nom_l or 'trust merchant' in nom_l:
            return static('images/paiements/tmb.webp')
        return ''


class HomeFeedLike(models.Model):
    """Like utilisateur sur une publication du fil d'accueil non-article."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='home_feed_likes',
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Like du fil d’accueil'
        verbose_name_plural = 'Likes du fil d’accueil'
        constraints = [
            models.UniqueConstraint(
                fields=('content_type', 'object_id', 'utilisateur'),
                name='home_feed_like_unique',
            ),
        ]

    def __str__(self):
        return f'{self.utilisateur} aime {self.content_object or "une publication"}'


class HomeFeedComment(models.Model):
    """Commentaire modéré sur une publication non-article du fil d'accueil."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='home_feed_comments',
    )
    texte = models.TextField(verbose_name='Commentaire')
    approuve = models.BooleanField(default=False, verbose_name='Approuvé')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Commentaire du fil d’accueil'
        verbose_name_plural = 'Commentaires du fil d’accueil'
        ordering = ['-date_creation']
        indexes = [
            models.Index(
                fields=('content_type', 'object_id', 'approuve'),
                name='core_hfc_content_approved_idx',
            ),
        ]

    def __str__(self):
        return f'{self.auteur} — {self.content_object or "publication"}'

