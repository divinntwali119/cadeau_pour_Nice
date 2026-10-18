from django.urls import path
from . import views

app_name = 'evenements'

urlpatterns = [
    path('', views.liste_evenements, name='liste'),
    path('<slug:slug>/', views.detail_evenement, name='detail'),
]
