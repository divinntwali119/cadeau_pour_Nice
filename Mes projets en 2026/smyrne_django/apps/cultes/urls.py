from django.urls import path
from . import views

app_name = 'cultes'

urlpatterns = [
    path('', views.liste_cultes, name='liste'),
]
