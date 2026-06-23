from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Candidato, Postulacion
# Create your views here.
def inicio(request):
    #Presentando en pantalla el contenido de inicio s
    return render(request, 'inicio.html')

def vistaLogin(request):
    return render(request, 'login.html')

def procesarLogin(request):
    usernameLogin = request.POST["username"]
    passwordLogin = request.POST["password"]

    usuarioAutenticado = authenticate(request, username=usernameLogin, password=passwordLogin)

    if usuarioAutenticado is not None:
        login(request, usuarioAutenticado)
        messages.success(request, 'Bienvenido/a ' + usuarioAutenticado.username)
        # Si es Reclutador (staff), va al dashboard de Reclutador
        if usuarioAutenticado.is_staff:
            return redirect('/listadoPostulaciones/')
        # Si es Candidato, va a su panel
        else:
            return redirect('/listadoCandidatos/')
    else:
        messages.error(request, 'Usuario o contraseña incorrectos')
        return redirect('/login/')

@login_required
def cerrarSesion(request):
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('/login/')

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

    # Datos para crear el usuario de login
    usernameNuevoCandidato = request.POST["username"]
    passwordNuevoCandidato = request.POST["password"]
    emailNuevoCandidato = request.POST["email"]

    # Creando el usuario con contraseña encriptada automáticamente
    nuevoUsuario = User.objects.create_user(
        username=usernameNuevoCandidato,
        password=passwordNuevoCandidato,
        email=emailNuevoCandidato
    )

    # Instanciar un objeto "Candidato" conectado a ese usuario
    nuevoCandidato = Candidato.objects.create(
        usuario=nuevoUsuario,
        nombre_completo=nombreCompletoNuevoCandidato,
        fecha_nacimiento=fechaNacimientoNuevoCandidato,
        genero=generoNuevoCandidato,
        nivel_estudios=nivelEstudiosNuevoCandidato,
        disponible_viajar=disponibleViajarNuevoCandidato,
        foto=fotoNuevoCandidato
    )
    messages.success(request, 'Candidato registrado exitosamente, ya puede iniciar sesión')
    return redirect('/login/')

@login_required
def listadoCandidatos(request):
    if request.user.is_staff:
        # El Reclutador ve a todos los candidatos
        candidatos = Candidato.objects.all()
    else:
        # El Candidato solo ve su propio perfil
        candidatos = Candidato.objects.filter(usuario=request.user)
    return render(request, 'candidato_listado.html', {'candidatos': candidatos})

@login_required
def editarCandidato(request, id):
    candidato = Candidato.objects.get(id=id)
    return render(request, 'candidato_editar.html', {'candidato': candidato})

@login_required
def actualizarCandidato(request, id):
    candidato = Candidato.objects.get(id=id)

    candidato.nombre_completo = request.POST["nombre_completo"]
    candidato.fecha_nacimiento = request.POST["fecha_nacimiento"]
    candidato.genero = request.POST["genero"]
    candidato.nivel_estudios = request.POST["nivel_estudios"]
    candidato.disponible_viajar = True if request.POST.get("disponible_viajar") else False

    # Solo se actualiza la foto si el usuario subió una nueva
    fotoEditada = request.FILES.get("foto")
    if fotoEditada:
        candidato.foto = fotoEditada

    candidato.save()
    messages.success(request, 'Candidato actualizado exitosamente')
    return redirect('/listadoCandidatos/')

@login_required
def eliminarCandidato(request, id):
    candidato = Candidato.objects.get(id=id)
    candidato.delete()
    messages.success(request, 'Candidato eliminado exitosamente')
    return redirect('/listadoCandidatos/')

# ---------------- POSTULACION ----------------
@login_required
def nuevaPostulacion(request):
    return render(request, 'postulacion_form.html')

@login_required
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

@login_required
def listadoPostulaciones(request):
    if request.user.is_staff:
        # El Reclutador ve todas las postulaciones
        postulaciones = Postulacion.objects.all()
    else:
        # El Candidato solo ve sus propias postulaciones
        candidatoActual = Candidato.objects.get(usuario=request.user)
        postulaciones = Postulacion.objects.filter(candidato=candidatoActual)
    return render(request, 'postulacion_listado.html', {'postulaciones': postulaciones})

@login_required
def editarPostulacion(request, id):
    postulacion = Postulacion.objects.get(id=id)
    candidatos = Candidato.objects.all()
    return render(request, 'postulacion_editar.html', {'postulacion': postulacion, 'candidatos': candidatos})

@login_required
def actualizarPostulacion(request, id):
    postulacion = Postulacion.objects.get(id=id)

    postulacion.vacante = request.POST["vacante"]
    postulacion.pretension_salarial = request.POST["pretension_salarial"]
    postulacion.estado = request.POST["estado"]

    # Solo se actualiza el PDF si el usuario subió uno nuevo
    cvEditado = request.FILES.get("cv_pdf")
    if cvEditado:
        postulacion.cv_pdf = cvEditado

    postulacion.save()
    messages.success(request, 'Postulación actualizada exitosamente')
    return redirect('/listadoPostulaciones/')

@login_required
def eliminarPostulacion(request, id):
    postulacion = Postulacion.objects.get(id=id)
    postulacion.delete()
    messages.success(request, 'Postulación eliminada exitosamente')
    return redirect('/listadoPostulaciones/')



def reporteVacantes(request):
    from django.db.models import Count, Avg

    # Contar cuántos candidatos se postularon por cada vacante
    postulaciones_por_vacante = Postulacion.objects.values('vacante').annotate(
        total=Count('id'),
        promedio_salario=Avg('pretension_salarial')
    )

    # Preparar los datos para mostrar en el template
    reporte = []
    for item in postulaciones_por_vacante:
        if item['vacante'] == 'DESARROLLADOR':
            nombre_vacante = 'Desarrollador'
        else:
            nombre_vacante = 'Diseñador'

        reporte.append({
            'vacante': nombre_vacante,
            'total': item['total'],
            'promedio_salario': round(item['promedio_salario'], 2) if item['promedio_salario'] else 0
        })

    # Total general de postulaciones
    total_general = Postulacion.objects.count()

    return render(request, 'reporte_vacantes.html', {
        'reporte': reporte,
        'total_general': total_general
    })