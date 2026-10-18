"""Vues — App Événements"""

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from .models import Evenement, InscriptionEvenement
from apps.core.security import is_rate_limited


def liste_evenements(request):
    """Liste des événements : à venir et passés séparés."""
    maintenant = timezone.now()
    context = {
        'evenements_a_venir': Evenement.objects.filter(publie=True, date_debut__gte=maintenant).order_by('date_debut'),
        'evenements_passes': Evenement.objects.filter(publie=True, date_debut__lt=maintenant).order_by('-date_debut')[:10],
    }
    return render(request, 'evenements/liste.html', context)


def detail_evenement(request, slug):
    """Détail d'un événement avec formulaire d'inscription sécurisé."""
    evenement = get_object_or_404(Evenement, slug=slug, publie=True)

    if request.method == 'POST' and evenement.inscriptions_ouvertes:
        # Protection bot : champ honeypot
        if request.POST.get('website'):
            return redirect('evenements:detail', slug=slug)

        # Rate limiting : max 10 inscriptions par 5 minutes par IP
        if is_rate_limited(request, key_prefix='evenement_inscr', limit=10, period=300):
            messages.warning(request, "⏳ Trop de tentatives. Veuillez patienter un instant.")
            return redirect('evenements:detail', slug=slug)

        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()

        if nom and prenom and email:
            obj, created = InscriptionEvenement.objects.get_or_create(
                evenement=evenement, email=email,
                defaults={'nom': nom, 'prenom': prenom, 'telephone': telephone}
            )
            if created:
                messages.success(request, f"✅ Inscription confirmée, {prenom} ! Nous vous attendons.")
            else:
                messages.warning(request, "⚠️ Vous êtes déjà inscrit(e) à cet événement.")
        else:
            messages.error(request, "❌ Veuillez remplir tous les champs obligatoires.")
        return redirect('evenements:detail', slug=slug)

    return render(request, 'evenements/detail.html', {'evenement': evenement})
