from django.urls import path
from . import views

app_name = 'galerie'

urlpatterns = [
    path('', views.liste_galerie, name='liste'),
]
