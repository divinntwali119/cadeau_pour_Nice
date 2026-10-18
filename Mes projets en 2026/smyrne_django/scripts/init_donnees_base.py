"""
Initialisation des données de base de l'Église 5e CELPA Smyrne :
- Paramètres du site (Nom, Coordonnées, Liens réseaux, Direct)
- Aucune coordonnée de paiement n'est préremplie : elles doivent être vérifiées dans l'administration.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smyrne.settings')
django.setup()

from apps.core.models import ParametreSite

def init_defaults():
    # 1. Paramètres du site
    param, created = ParametreSite.objects.get_or_create(pk=1, defaults={
        'nom_eglise': '5e CELPA SMYRNE',
        'slogan': "Une communauté chrétienne vivante engagée dans la prédication de l'Évangile, l'édification de la foi et le service dans la ville de Bukavu.",
        'adresse': 'Avenue de la Paix, Commune d\'Ibanda, Ville de Bukavu, Sud-Kivu, RDC',
        'telephone': '',
        'email': '',
        'whatsapp': '',
        'facebook': 'https://facebook.com/5celpasmyrne',
        'youtube': 'https://youtube.com/@5celpasmyrne',
        'en_direct_actif': False,
        'en_direct_titre': 'Culte Dominical en Direct — Louange & Prédication',
        'en_direct_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    })
    if created:
        print("✅ Paramètres du site créés avec succès.")
    else:
        print("ℹ️ Paramètres du site déjà existants.")

    # Les coordonnées de paiement sont saisies et vérifiées dans l'administration.
    print("ℹ️ Configurez les moyens de don vérifiés dans l'administration Django.")

if __name__ == '__main__':
    init_defaults()
