from django.shortcuts import render
from .models import Culte


def liste_cultes(request):
    """Liste de tous les cultes actifs, groupés par type."""
    cultes = Culte.objects.filter(actif=True).order_by('ordre', 'jour', 'heure_debut')
    # Grouper par type de culte
    types = {}
    for culte in cultes:
        types.setdefault(culte.get_type_culte_display(), []).append(culte)
    context = {
        'cultes': cultes,
        'types_cultes': types,
        'culte_en_direct': Culte.objects.filter(est_en_direct=True).first(),
    }
    return render(request, 'cultes/liste.html', context)
