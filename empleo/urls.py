from django.urls import path  
from . import views

urlpatterns = [
    path('', views.inicio),
    path('login/', views.vistaLogin),
    path('procesarLogin/', views.procesarLogin),
    path('cerrarSesion/', views.cerrarSesion),


    path('nuevoCandidato/', views.nuevoCandidato),
    path('registrar_candidato/', views.nuevoCandidato),
    path('guardarCandidato/', views.guardarCandidato),
    path('listadoCandidatos/', views.listadoCandidatos),
    path('editarCandidato/<int:id>/', views.editarCandidato),
    path('actualizarCandidato/<int:id>/', views.actualizarCandidato),
    path('eliminarCandidato/<int:id>/', views.eliminarCandidato),


    path('nuevaPostulacion/', views.nuevaPostulacion),
    path('postulacion_form/', views.nuevaPostulacion),
    path('guardarPostulacion/', views.guardarPostulacion),
    path('listadoPostulaciones/', views.listadoPostulaciones),
    path('editarPostulacion/<int:id>/', views.editarPostulacion),
    path('actualizarPostulacion/<int:id>/', views.actualizarPostulacion),
    path('eliminarPostulacion/<int:id>/', views.eliminarPostulacion),

   
    path('reporteVacantes/', views.reporteVacantes),
    path('verPDF/<int:id>/', views.verPDF, name='verPDF'),

]