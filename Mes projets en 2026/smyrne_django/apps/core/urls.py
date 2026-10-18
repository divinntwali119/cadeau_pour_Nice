"""URLs — App Core"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('fil/<str:kind>/<int:object_id>/like/', views.toggle_feed_like, name='feed_like'),
    path('fil/<str:kind>/<int:object_id>/commenter/', views.create_feed_comment, name='feed_comment'),
    # PWA
    path('offline/', views.offline, name='offline'),
    # Recherche & Dons
    path('recherche-globale/', views.recherche_globale, name='recherche_globale'),
    path('dons/', views.dons, name='dons'),
    # SEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]
