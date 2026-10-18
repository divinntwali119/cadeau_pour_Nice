from django.urls import path
from . import views

app_name = 'ministeres'

urlpatterns = [
    path('', views.index_ministeres, name='index'),
]
