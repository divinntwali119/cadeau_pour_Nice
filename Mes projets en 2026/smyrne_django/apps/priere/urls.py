from django.urls import path
from . import views

app_name = 'priere'

urlpatterns = [
    path('', views.index_priere, name='index'),
]
