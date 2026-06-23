from django.db import models

# Create your models here.
from django.contrib.auth.models import User #Esto nos permite conectar el modelo Candidato con el sistema de usuarios de Django (necesario para el login).
from django.core.validators import FileExtensionValidator


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
    foto = models.FileField(
        upload_to='empleo',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    nombre_completo = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=GENERO_OPCIONES)
    nivel_estudios = models.CharField(max_length=10, choices=NIVEL_ESTUDIOS_OPCIONES)
    disponible_viajar = models.BooleanField(default=False)

class Postulacion(models.Model):
    VACANTE_OPCIONES = [
        ('DESARROLLADOR', 'Desarrollador'),
        ('DISENADOR', 'Diseñador'),
    ]

    ESTADO_OPCIONES = [
        ('PENDIENTE', 'Pendiente'),
        ('PRESELECCIONADO', 'Preseleccionado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='postulaciones')
    cv_pdf = models.FileField(
        upload_to='cvs_postulaciones/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    vacante = models.CharField(max_length=20, choices=VACANTE_OPCIONES)
    fecha_postulacion = models.DateField(auto_now_add=True)
    pretension_salarial = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_OPCIONES, default='PENDIENTE')
