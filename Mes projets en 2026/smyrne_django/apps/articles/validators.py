"""Validation et intégration sécurisée des vidéos d'actualités."""

import re
from urllib.parse import parse_qs, urlparse

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


_VIDEO_ID = re.compile(r'^[A-Za-z0-9_-]{11}$')
_VIMEO_ID = re.compile(r'^\d{6,12}$')


def get_video_embed_url(value):
    """Retourne uniquement une URL d'intégration YouTube/Vimeo approuvée."""
    if not value:
        return ''

    try:
        parsed = urlparse(value.strip())
        hostname = (parsed.hostname or '').lower().rstrip('.')
    except (AttributeError, ValueError):
        return ''

    if parsed.scheme.lower() not in {'http', 'https'} or not hostname:
        return ''
    if parsed.username or parsed.password:
        return ''

    path_parts = [part for part in parsed.path.split('/') if part]
    video_id = ''

    if hostname in {'youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtube-nocookie.com', 'www.youtube-nocookie.com'}:
        if parsed.path.rstrip('/') == '/watch':
            video_id = parse_qs(parsed.query).get('v', [''])[0]
        elif len(path_parts) >= 2 and path_parts[0] in {'embed', 'shorts', 'live', 'v'}:
            video_id = path_parts[1]
        if _VIDEO_ID.fullmatch(video_id):
            return f'https://www.youtube-nocookie.com/embed/{video_id}'

    elif hostname == 'youtu.be' and path_parts and _VIDEO_ID.fullmatch(path_parts[0]):
        return f'https://www.youtube-nocookie.com/embed/{path_parts[0]}'

    elif hostname in {'vimeo.com', 'www.vimeo.com', 'player.vimeo.com'} and path_parts:
        if hostname == 'player.vimeo.com':
            if len(path_parts) == 2 and path_parts[0] == 'video':
                video_id = path_parts[1]
        else:
            video_id = path_parts[-1]
        if _VIMEO_ID.fullmatch(video_id):
            return f'https://player.vimeo.com/video/{video_id}'

    return ''


def validate_video_url(value):
    """N'autorise que les URL de vidéos YouTube ou Vimeo intégrables."""
    if value and not get_video_embed_url(value):
        raise ValidationError(
            _('Utilisez un lien vidéo YouTube ou Vimeo valide, ou téléversez un fichier vidéo.')
        )
