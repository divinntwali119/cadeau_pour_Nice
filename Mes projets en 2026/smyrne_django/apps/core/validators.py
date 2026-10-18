"""
=============================================================
VALIDATEURS — Sécurité des fichiers et téléversements
=============================================================
Validation stricte des extensions, tailles et types réels de fichiers
pour éviter tout téléversement de contenu malveillant.
"""

import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image


def validate_file_size(file, max_mb=10):
    """Vérifie que la taille du fichier ne dépasse pas max_mb mégaoctets."""
    max_size_bytes = max_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(
            _(f"La taille du fichier ({file.size / (1024*1024):.1f} Mo) dépasse la limite autorisée de {max_mb} Mo.")
        )


def validate_image_file(file, max_mb=5):
    """
    Valide une image :
    1. Taille maximale
    2. Extension autorisée (.jpg, .jpeg, .png, .webp)
    3. Intégrité via PIL pour s'assurer que c'est une image réelle
    """
    validate_file_size(file, max_mb=max_mb)

    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if ext not in allowed_extensions:
        raise ValidationError(
            _(f"Format d'image non supporté ({ext}). Formats autorisés : JPG, PNG, WEBP.")
        )

    # Vérification du contenu réel de l'image
    try:
        image = Image.open(file)
        image.verify()
    except Exception:
        raise ValidationError(_("Le fichier téléversé n'est pas une image valide ou est corrompu."))


def validate_audio_file(file, max_mb=50):
    """Valide un fichier audio (extension et taille)."""
    validate_file_size(file, max_mb=max_mb)
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
    if ext not in allowed_extensions:
        raise ValidationError(
            _(f"Format audio non supporté ({ext}). Formats autorisés : MP3, WAV, OGG, M4A.")
        )


def validate_video_file(file, max_mb=100):
    """Valide un fichier vidéo (extension et taille)."""
    validate_file_size(file, max_mb=max_mb)
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.mp4', '.webm', '.mov']
    if ext not in allowed_extensions:
        raise ValidationError(
            _(f"Format vidéo non supporté ({ext}). Formats autorisés : MP4, WEBM, MOV.")
        )
