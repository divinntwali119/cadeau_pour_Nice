"""
=============================================================
SÉCURITÉ — Utilitaires de protection & Rate Limiting
=============================================================
Rate limiting basé sur le cache Django (IP ou session)
et détection anti-spam pour les formulaires publics.
"""

from django.core.cache import cache


def get_client_ip(request):
    """Récupère l'adresse IP réelle du client."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def is_rate_limited(request, key_prefix='rl', limit=5, period=60):
    """
    Vérifie si une requête dépasse la limite autorisée.
    - limit: nombre maximal de requêtes autorisées
    - period: période en secondes (ex: 60s)
    Retourne True si la limite est dépassée (bloqué), False sinon.
    """
    ip = get_client_ip(request)
    cache_key = f"rate_limit:{key_prefix}:{ip}"

    # Récupérer le compteur actuel
    current = cache.get(cache_key, 0)
    if current >= limit:
        return True

    # Incrémenter et définir le timeout
    try:
        cache.set(cache_key, current + 1, timeout=period)
    except Exception:
        pass

    return False
