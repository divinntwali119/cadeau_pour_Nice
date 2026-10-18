from django.urls import path
from . import views

app_name = 'predications'

urlpatterns = [
    path('', views.liste_predications, name='liste'),
    path('<slug:slug>/', views.detail_predication, name='detail'),
]
