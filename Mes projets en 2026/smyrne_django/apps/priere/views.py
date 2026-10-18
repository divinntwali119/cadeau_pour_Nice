"""Vues — App Prière"""

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DemandePriere, TemoignagePriere
from apps.core.security import is_rate_limited


def index_priere(request):
    """Page prière avec formulaires et témoignages."""
    temoignages = TemoignagePriere.objects.filter(approuve=True).order_by('-date_creation')[:10]

    if request.method == 'POST':
        # Protection Honeypot anti-spam : si le champ caché "website" est rempli, c'est un bot
        if request.POST.get('website'):
            # Ignorer silencieusement le robot
            return redirect('priere:index')

        # Rate limiting : max 5 soumissions par tranche de 5 minutes par IP
        if is_rate_limited(request, key_prefix='priere', limit=5, period=300):
            messages.warning(
                request,
                "⏳ Trop de demandes envoyées récemment. Veuillez patienter quelques minutes avant de réessayer."
            )
            return redirect('priere:index')

        form_type = request.POST.get('form_type')

        if form_type == 'demande':
            nom = request.POST.get('nom', '').strip()
            sujet = request.POST.get('sujet', '').strip()
            message = request.POST.get('message', '').strip()
            if nom and sujet and message:
                DemandePriere.objects.create(
                    nom=nom,
                    email=request.POST.get('email', '').strip(),
                    sujet=sujet,
                    message=message,
                    confidentiel='confidentiel' in request.POST,
                )
                messages.success(request, "🙏 Votre demande de prière a été soumise. Nous prions pour vous !")
            else:
                messages.error(request, "❌ Veuillez remplir tous les champs obligatoires.")

        elif form_type == 'temoignage':
            nom = request.POST.get('nom', '').strip()
            texte = request.POST.get('texte', '').strip()
            if nom and texte:
                TemoignagePriere.objects.create(nom=nom, texte=texte)
                messages.success(request, "🙌 Merci pour votre témoignage ! Il sera affiché après validation.")
            else:
                messages.error(request, "❌ Veuillez remplir tous les champs.")

        return redirect('priere:index')

    return render(request, 'priere/index.html', {'temoignages': temoignages})
