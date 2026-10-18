"""
=============================================================
VUES — App Accounts (Connexion / Inscription / Déconnexion)
=============================================================
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .forms import ConnexionForm, InscriptionForm
from .models import ProfilMembre
from apps.core.security import is_rate_limited
from apps.core.validators import validate_image_file


def connexion(request):
    """Connexion — Membres + Administrateurs."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        return redirect('accounts:profil')

    form = ConnexionForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Bienvenue, {user.first_name or user.username} !")
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and next_url != request.path:
                return redirect(next_url)
            if user.is_staff:
                return redirect('/admin/')
            return redirect('accounts:profil')
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect. Veuillez réessayer.")

    return render(request, 'accounts/connexion.html', {'form': form})


def inscription(request):
    """Inscription d'un nouveau membre avec rate limiting."""
    if request.user.is_authenticated:
        return redirect('accounts:profil')

    form = InscriptionForm(request.POST or None)

    if request.method == 'POST':
        # Rate limiting : max 3 inscriptions par heure par adresse IP
        if is_rate_limited(request, key_prefix='inscription', limit=3, period=3600):
            messages.error(
                request,
                "⏳ Limite de création de comptes atteinte pour le moment. Veuillez réessayer plus tard."
            )
            return render(request, 'accounts/inscription.html', {'form': form})

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()

            # Mettre à jour le profil créé par le signal
            tel = form.cleaned_data.get('telephone', '').strip()
            ProfilMembre.objects.filter(utilisateur=user).update(telephone=tel)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Votre compte a été créé avec succès ! Bienvenue, {user.first_name or user.username} !")
            return redirect('accounts:profil')
        else:
            messages.error(request, "Veuillez corriger les erreurs indiquées ci-dessous.")

    return render(request, 'accounts/inscription.html', {'form': form})


def deconnexion(request):
    """Déconnexion."""
    logout(request)
    messages.info(request, "Vous avez été déconnecté(e). À bientôt !")
    return redirect('core:accueil')


@login_required
def profil(request):
    """Page de profil du membre connecté."""
    profil_obj, _ = ProfilMembre.objects.get_or_create(utilisateur=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()

        # Validation de l'image de profil
        if 'photo' in request.FILES:
            photo_file = request.FILES['photo']
            try:
                validate_image_file(photo_file, max_mb=5)
                profil_obj.photo = photo_file
            except ValidationError as e:
                messages.error(request, f"❌ Erreur sur la photo : {e.message}")
                return render(request, 'accounts/profil.html', {'profil': profil_obj})

        request.user.save()
        profil_obj.telephone = request.POST.get('telephone', '').strip()
        profil_obj.bio = request.POST.get('bio', '').strip()
        profil_obj.save()

        messages.success(request, "Votre profil a été mis à jour avec succès !")
        return redirect('accounts:profil')

    return render(request, 'accounts/profil.html', {'profil': profil_obj})
