"""Vues — App Ministères"""

from django.shortcuts import render
from .models import Ministere, Departement, Chorale, Pasteur


def index_ministeres(request):
    """Page Ministères, Départements et Chorales."""
    return render(request, 'ministeres/index.html', {
        'ministeres': Ministere.objects.filter(actif=True).prefetch_related('departements').order_by('ordre'),
        'chorales': Chorale.objects.filter(actif=True).order_by('ordre'),
        'pasteur': Pasteur.objects.filter(actif=True).first(),
    })
