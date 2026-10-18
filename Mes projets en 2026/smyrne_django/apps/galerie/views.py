"""Vues — App Galerie"""

from django.shortcuts import render, get_object_or_404
from .models import PhotoGalerie, CategorieGalerie


def liste_galerie(request):
    """Galerie photos avec filtre par catégorie."""
    categorie_slug = request.GET.get('categorie')
    photos = PhotoGalerie.objects.filter(publie=True).order_by('-date_ajout')
    categorie_active = None

    if categorie_slug:
        categorie_active = get_object_or_404(CategorieGalerie, slug=categorie_slug)
        photos = photos.filter(categorie=categorie_active)

    return render(request, 'galerie/liste.html', {
        'photos': photos,
        'categories': CategorieGalerie.objects.all(),
        'categorie_active': categorie_active,
    })
