"""
=============================================================
URLS PRINCIPAL — Projet 5e CELPA SMYRNE
=============================================================
Routes principales du site. Chaque app a ses propres urls.py.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os
from apps.core import views as core_views

# Personnalisation du titre de l'admin
admin.site.site_header = '5e CELPA SMYRNE — Administration'
admin.site.site_title = 'Smyrne Admin'
admin.site.index_title = 'Tableau de bord'

urlpatterns = [
    # ─── Interface d'administration ───
    path('admin/', admin.site.urls),

    # ─── CKEditor (upload d'images) ───
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # ─── PWA (doivent être servis depuis la racine pour la portée PWA) ───
    path('sw.js', core_views.service_worker, name='service_worker'),
    path('manifest.json', core_views.manifest_json, name='manifest_json'),

    # ─── Pages publiques ───
    path('', include('apps.core.urls')),                     # Accueil
    path('cultes/', include('apps.cultes.urls')),            # Cultes
    path('predications/', include('apps.predications.urls')), # Prédications
    path('actualites/', include('apps.articles.urls')),      # Actualités
    path('evenements/', include('apps.evenements.urls')),    # Événements
    path('galerie/', include('apps.galerie.urls')),          # Galerie
    path('priere/', include('apps.priere.urls')),            # Prière
    path('notre-histoire/', include('apps.histoire.urls')),  # Notre Histoire
    path('ministeres/', include('apps.ministeres.urls')),    # Ministères
    path('', include('apps.accounts.urls')),                 # Connexion / Déconnexion
]

# ─── Gestionnaires d'erreurs personnalisés ───
from apps.core.views import handler400, handler403, handler404, handler500  # noqa
handler400 = handler400  # noqa
handler403 = handler403  # noqa
handler404 = handler404  # noqa
handler500 = handler500  # noqa

# ─── Servir les médias en développement ───
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
