from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Candidato, Postulacion

# Create your views here.
def inicio(request):
    #Presentando en pantalla el contenido de inicio s
    return render(request, 'inicio.html')

def nuevoCandidato(request):
    return render(request, 'registrar_candidato.html')


def guardarCandidato(request):
    # Capturando valores via método POST
    nombreCompletoNuevoCandidato = request.POST["nombre_completo"]
    fechaNacimientoNuevoCandidato = request.POST["fecha_nacimiento"]
    generoNuevoCandidato = request.POST["genero"]
    nivelEstudiosNuevoCandidato = request.POST["nivel_estudios"]
    # El checkbox solo llega si fue marcado, por eso usamos .get()
    disponibleViajarNuevoCandidato = True if request.POST.get("disponible_viajar") else False

    # Capturando el archivo de name="foto"
    fotoNuevoCandidato = request.FILES.get("foto")

    # Instanciar un objeto "Candidato"
    nuevoCandidato = Candidato.objects.create(
        nombre_completo=nombreCompletoNuevoCandidato,
        fecha_nacimiento=fechaNacimientoNuevoCandidato,
        genero=generoNuevoCandidato,
        nivel_estudios=nivelEstudiosNuevoCandidato,
        disponible_viajar=disponibleViajarNuevoCandidato,
        foto=fotoNuevoCandidato
    )

    messages.success(request, 'Candidato registrado exitosamente')
    return redirect('/listadoCandidatos/')


def listadoCandidatos(request):
    candidatos = Candidato.objects.all()
    return render(request, 'candidato_listado.html', {'candidatos': candidatos})


# ---------------- POSTULACION ----------------

def nuevaPostulacion(request):
    return render(request, 'postulacion_form.html')


def guardarPostulacion(request):
    # Capturando valores via método POST
    vacanteNuevaPostulacion = request.POST["vacante"]
    pretensionSalarialNuevaPostulacion = request.POST["pretension_salarial"]

    # Capturando el archivo de name="cv_pdf"
    cvPdfNuevaPostulacion = request.FILES.get("cv_pdf")

    # El candidato se asigna según el usuario logueado
    candidatoActual = Candidato.objects.get(usuario=request.user)

    # Instanciar un objeto "Postulacion"
    nuevaPostulacion = Postulacion.objects.create(
        candidato=candidatoActual,
        vacante=vacanteNuevaPostulacion,
        pretension_salarial=pretensionSalarialNuevaPostulacion,
        cv_pdf=cvPdfNuevaPostulacion
    )

    messages.success(request, 'Postulación enviada exitosamente')
    return redirect('/listadoPostulaciones/')


def listadoPostulaciones(request):
    postulaciones = Postulacion.objects.all()
    return render(request, 'postulacion_listado.html', {'postulaciones': postulaciones})