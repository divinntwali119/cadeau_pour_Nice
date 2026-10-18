from django.urls import path
from . import views

app_name = 'histoire'

urlpatterns = [
    path('', views.index_histoire, name='index'),
    path('biographie/', views.index_biographie, name='biographie'),
]
