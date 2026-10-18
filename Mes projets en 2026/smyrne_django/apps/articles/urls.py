from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.liste_articles, name='liste'),
    path('<slug:slug>/', views.detail_article, name='detail'),
    path('<slug:slug>/like/', views.toggle_like, name='like'),
]
