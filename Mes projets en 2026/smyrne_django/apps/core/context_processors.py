from .models import ParametreSite
from .verset_du_jour import get_verset_du_jour


def parametres_site(request):
    """Injecte les paramètres du site et le verset du jour dans chaque template."""
    try:
        params = ParametreSite.objects.get(pk=1)
    except ParametreSite.DoesNotExist:
        params = None

    return {
        'parametres_site': params,
        'verset_du_jour': get_verset_du_jour(),
    }
