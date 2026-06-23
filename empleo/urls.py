from django.urls import path  

from . import views

urlpatterns = [
    path('', views.inicio),
    path('registrar_candidato/', views.nuevoCandidato),
]