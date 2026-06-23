from django.db import models

# Create your models here.
from django.contrib.auth.models import User #Esto nos permite conectar el modelo Candidato con el sistema de usuarios de Django (necesario para el login).

class Candidato(models.Model):
    GENERO_OPCIONES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    NIVEL_ESTUDIOS_OPCIONES = [
        ('GRADO', 'Grado'),
        ('MASTER', 'Máster'),
        ('DOCTORADO', 'Doctorado'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
#OneToOneField(User, ...) → significa "cada Candidato está ligado a exactamente UN usuario del sistema, y viceversa". Así, cuando alguien se registra y hace login, ese usuario tiene su perfil de Candidato asociado.
    foto = models.FileField(upload_to='empleo',null=True,blank=True)
    nombre_completo = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=GENERO_OPCIONES)
    nivel_estudios = models.CharField(max_length=10, choices=NIVEL_ESTUDIOS_OPCIONES)
    disponible_viajar = models.BooleanField(default=False)

  