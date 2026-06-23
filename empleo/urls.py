from django.urls import path  

from . import views

urlpatterns = [
    path('', views.inicio),
    path('registrar_candidato/', views.nuevoCandidato),
    path('guardarCandidato/', views.guardarCandidato),
    path('listadoCandidatos/', views.listadoCandidatos),
    path('editarCandidato/<int:id>/', views.editarCandidato),
    path('actualizarCandidato/<int:id>/', views.actualizarCandidato),
    path('eliminarCandidato/<int:id>/', views.eliminarCandidato),

    # ---------------- POSTULACION ----------------
    path('postulacion_form/', views.nuevaPostulacion),
    path('guardarPostulacion/', views.guardarPostulacion),
    path('listadoPostulaciones/', views.listadoPostulaciones),
    path('editarPostulacion/<int:id>/', views.editarPostulacion),
    path('actualizarPostulacion/<int:id>/', views.actualizarPostulacion),
    path('eliminarPostulacion/<int:id>/', views.eliminarPostulacion),
]



