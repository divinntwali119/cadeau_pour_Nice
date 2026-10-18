"""Vues — App Histoire"""

from django.shortcuts import render
from .models import ChoraleHistorique, BlocBiographie


def index_histoire(request):
    """Page Notre Histoire."""
    return render(request, 'histoire/index.html', {
        'chorales_historiques': ChoraleHistorique.objects.all().order_by('ordre'),
    })


def index_biographie(request):
    """Page Biographie du pasteur actuel."""
    blocs = BlocBiographie.objects.all().order_by('ordre')
    timeline = blocs.filter(type_bloc='timeline')
    autres_blocs = blocs.exclude(type_bloc='timeline')
    return render(request, 'biographie/index.html', {
        'blocs': blocs,
        'timeline': timeline,
        'autres_blocs': autres_blocs,
    })
