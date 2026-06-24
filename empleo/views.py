from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from .models import Candidato, Postulacion
from django.http import FileResponse
import os


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
    from datetime import date
    return render(request, 'registrar_candidato.html', {'hoy': date.today().strftime('%Y-%m-%d')})

def guardarCandidato(request):
    # Capturando valores via método POST con .get() para evitar KeyError
    nombreCompletoNuevoCandidato = request.POST.get("nombre_completo", "").strip()
    fechaNacimientoNuevoCandidato = request.POST.get("fecha_nacimiento", "")
    generoNuevoCandidato = request.POST.get("genero", "")
    nivelEstudiosNuevoCandidato = request.POST.get("nivel_estudios", "")
    disponibleViajarNuevoCandidato = True if request.POST.get("disponible_viajar") else False
    usernameNuevoCandidato = request.POST.get("username", "").strip()
    passwordNuevoCandidato = request.POST.get("password", "")
    emailNuevoCandidato = request.POST.get("email", "").strip()

    # Validación de campos obligatorios en el servidor
    if not nombreCompletoNuevoCandidato:
        messages.error(request, 'El nombre completo es obligatorio')
        return redirect('/nuevoCandidato/')
    if not fechaNacimientoNuevoCandidato:
        messages.error(request, 'La fecha de nacimiento es obligatoria')
        return redirect('/nuevoCandidato/')
    # Validar que la fecha no sea futura
    from datetime import date
    try:
        from datetime import datetime
        fecha_parsed = datetime.strptime(fechaNacimientoNuevoCandidato, '%Y-%m-%d').date()
        if fecha_parsed >= date.today():
            messages.error(request, 'La fecha de nacimiento no puede ser hoy ni una fecha futura')
            return redirect('/nuevoCandidato/')
    except ValueError:
        messages.error(request, 'La fecha de nacimiento no tiene un formato válido')
        return redirect('/nuevoCandidato/')
    if not generoNuevoCandidato:
        messages.error(request, 'Debe seleccionar un género')
        return redirect('/nuevoCandidato/')
    if not nivelEstudiosNuevoCandidato:
        messages.error(request, 'Debe seleccionar el nivel de estudios')
        return redirect('/nuevoCandidato/')
    if not usernameNuevoCandidato:
        messages.error(request, 'El nombre de usuario es obligatorio')
        return redirect('/nuevoCandidato/')
    if not passwordNuevoCandidato:
        messages.error(request, 'La contraseña es obligatoria')
        return redirect('/nuevoCandidato/')
    if not emailNuevoCandidato:
        messages.error(request, 'El correo electrónico es obligatorio')
        return redirect('/nuevoCandidato/')

    # Validar que el username no esté ya en uso
    if User.objects.filter(username=usernameNuevoCandidato).exists():
        messages.error(request, 'El nombre de usuario ya está en uso, elija otro')
        return redirect('/nuevoCandidato/')

    # Capturando el archivo de name="foto"
    fotoNuevoCandidato = request.FILES.get("foto")

    # Validar extensión de la foto si fue subida
    if fotoNuevoCandidato:
        extensiones_permitidas = ['jpg', 'jpeg', 'png']
        extension = fotoNuevoCandidato.name.split('.')[-1].lower()
        if extension not in extensiones_permitidas:
            messages.error(request, 'Solo se permiten imágenes en formato JPG, JPEG o PNG')
            return redirect('/nuevoCandidato/')

    # Creando el usuario con contraseña encriptada automáticamente
    nuevoUsuario = User.objects.create_user(
        username=usernameNuevoCandidato,
        password=passwordNuevoCandidato,
        email=emailNuevoCandidato
    )

    # Instanciar un objeto "Candidato" conectado a ese usuario
    Candidato.objects.create(
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
    return render(request, 'listadoCandidatos.html', {'candidatos': candidatos})

@login_required
def editarCandidato(request, id):
    from datetime import date
    candidato = Candidato.objects.get(id=id)
    return render(request, 'candidato_editar.html', {
        'candidato': candidato,
        'hoy': date.today().strftime('%Y-%m-%d')
    })

@login_required
def actualizarCandidato(request, id):
    candidato = Candidato.objects.get(id=id)

    # Capturando con .get() para evitar KeyError si algún campo no llega
    nombreCompleto   = request.POST.get("nombre_completo", "").strip()
    fechaNacimiento  = request.POST.get("fecha_nacimiento", "")
    genero           = request.POST.get("genero", "")
    nivelEstudios    = request.POST.get("nivel_estudios", "")

    # Validación de campos obligatorios en el servidor
    if not nombreCompleto:
        messages.error(request, 'El nombre completo es obligatorio')
        return redirect('/editarCandidato/' + str(id) + '/')
    if not fechaNacimiento:
        messages.error(request, 'La fecha de nacimiento es obligatoria')
        return redirect('/editarCandidato/' + str(id) + '/')
    # Validar que la fecha no sea futura
    from datetime import date, datetime
    try:
        fecha_parsed = datetime.strptime(fechaNacimiento, '%Y-%m-%d').date()
        if fecha_parsed >= date.today():
            messages.error(request, 'La fecha de nacimiento no puede ser hoy ni una fecha futura')
            return redirect('/editarCandidato/' + str(id) + '/')
    except ValueError:
        messages.error(request, 'La fecha de nacimiento no tiene un formato válido')
        return redirect('/editarCandidato/' + str(id) + '/')
    if not genero:
        messages.error(request, 'Debe seleccionar un género')
        return redirect('/editarCandidato/' + str(id) + '/')
    if not nivelEstudios:
        messages.error(request, 'Debe seleccionar el nivel de estudios')
        return redirect('/editarCandidato/' + str(id) + '/')

    candidato.nombre_completo   = nombreCompleto
    candidato.fecha_nacimiento  = fechaNacimiento
    candidato.genero            = genero
    candidato.nivel_estudios    = nivelEstudios
    candidato.disponible_viajar = True if request.POST.get("disponible_viajar") else False

    # Solo se actualiza la foto si el usuario subió una nueva
    fotoEditada = request.FILES.get("foto")
    if fotoEditada:
        # Validar extensión del archivo en el servidor
        extensiones_permitidas = ['jpg', 'jpeg', 'png']
        extension = fotoEditada.name.split('.')[-1].lower()
        if extension not in extensiones_permitidas:
            messages.error(request, 'Solo se permiten imágenes en formato JPG, JPEG o PNG')
            return redirect('/editarCandidato/' + str(id) + '/')

        # Si ya existía una foto anterior, la eliminamos del disco antes de reemplazarla
        if candidato.foto:
            ruta_foto_anterior = candidato.foto.path
            if os.path.isfile(ruta_foto_anterior):
                os.remove(ruta_foto_anterior)

        candidato.foto = fotoEditada

    candidato.save()
    messages.success(request, 'Candidato actualizado exitosamente')
    return redirect('/listadoCandidatos/')

@login_required
def eliminarCandidato(request, id):
    candidatoAEliminar = Candidato.objects.get(id=id)

    # Si el candidato tiene una foto asociada, eliminarla del disco
    if candidatoAEliminar.foto:
        ruta_foto = candidatoAEliminar.foto.path
        if os.path.isfile(ruta_foto):
            os.remove(ruta_foto)

    candidatoAEliminar.delete()
    messages.success(request, 'Candidato eliminado exitosamente')
    return redirect('/listadoCandidatos/')

# ---------------- POSTULACION ----------------
@login_required
def nuevaPostulacion(request):
    return render(request, 'postulacion_form.html')

@login_required
def guardarPostulacion(request):
    # Capturando con .get() para evitar KeyError
    vacanteNuevaPostulacion = request.POST.get("vacante", "")
    pretensionSalarialNuevaPostulacion = request.POST.get("pretension_salarial", "").strip()
    cvPdfNuevaPostulacion = request.FILES.get("cv_pdf")

    # Validación de campos obligatorios en el servidor
    if not vacanteNuevaPostulacion:
        messages.error(request, 'Debe seleccionar la vacante a la que aplica')
        return redirect('/nuevaPostulacion/')
    if not pretensionSalarialNuevaPostulacion:
        messages.error(request, 'La pretensión salarial es obligatoria')
        return redirect('/nuevaPostulacion/')
    if not cvPdfNuevaPostulacion:
        messages.error(request, 'Debe adjuntar su Currículum Vitae en formato PDF')
        return redirect('/nuevaPostulacion/')

    # Validar extensión del CV en el servidor
    extension = cvPdfNuevaPostulacion.name.split('.')[-1].lower()
    if extension != 'pdf':
        messages.error(request, 'El Currículum Vitae debe estar en formato PDF')
        return redirect('/nuevaPostulacion/')

    # El candidato se asigna según el usuario logueado
    candidatoActual = Candidato.objects.get(usuario=request.user)
    # Instanciar un objeto "Postulacion"
    Postulacion.objects.create(
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
    return render(request, 'listadoPostulaciones.html', {'postulaciones': postulaciones})

@login_required
def editarPostulacion(request, id):
    postulacion = Postulacion.objects.get(id=id)
    candidatos = Candidato.objects.all()
    return render(request, 'postulacion_editar.html', {'postulacion': postulacion, 'candidatos': candidatos})

@login_required
def actualizarPostulacion(request, id):
    postulacion = Postulacion.objects.get(id=id)

    # Capturando con .get() para evitar KeyError
    vacante            = request.POST.get("vacante", "")
    pretensionSalarial = request.POST.get("pretension_salarial", "").strip()

    # Validación de campos obligatorios en el servidor
    if not vacante:
        messages.error(request, 'Debe seleccionar la vacante')
        return redirect('/editarPostulacion/' + str(id) + '/')
    if not pretensionSalarial:
        messages.error(request, 'La pretensión salarial es obligatoria')
        return redirect('/editarPostulacion/' + str(id) + '/')

    postulacion.vacante             = vacante
    postulacion.pretension_salarial = pretensionSalarial

    # Solo el reclutador puede cambiar el estado
    if request.user.is_staff:
        postulacion.estado = request.POST.get("estado", postulacion.estado)

    # Solo se actualiza el PDF si el usuario subió uno nuevo
    nuevoCv = request.FILES.get("cv_pdf")
    if nuevoCv:
        # Validar extensión del CV en el servidor
        extension = nuevoCv.name.split('.')[-1].lower()
        if extension != 'pdf':
            messages.error(request, 'El Currículum Vitae debe estar en formato PDF')
            return redirect('/editarPostulacion/' + str(id) + '/')

        # Si ya existía un CV anterior, lo eliminamos del disco antes de reemplazarlo
        if postulacion.cv_pdf:
            ruta_cv_anterior = postulacion.cv_pdf.path
            if os.path.isfile(ruta_cv_anterior):
                os.remove(ruta_cv_anterior)

        postulacion.cv_pdf = nuevoCv

    postulacion.save()
    messages.success(request, 'Postulación actualizada exitosamente')
    return redirect('/listadoPostulaciones/')

@login_required
def eliminarPostulacion(request, id):
    postulacionAEliminar = Postulacion.objects.get(id=id)

    # Si la postulación tiene un CV asociado, eliminarlo del disco
    if postulacionAEliminar.cv_pdf:
        ruta_cv = postulacionAEliminar.cv_pdf.path
        if os.path.isfile(ruta_cv):
            os.remove(ruta_cv)

    postulacionAEliminar.delete()
    messages.success(request, 'Postulación eliminada exitosamente')
    return redirect('/listadoPostulaciones/')

def verPDF(request, id):
    postulacion = Postulacion.objects.get(id=id)
    ruta = postulacion.cv_pdf.path
    return FileResponse(open(ruta, 'rb'), content_type='application/pdf')

@login_required
def reporteVacantes(request):
    # Agrupamos las postulaciones por vacante, contando cuántas hay
    # y calculando el promedio de pretensión salarial de cada una
    reporte = Postulacion.objects.values('vacante').annotate(
        total_postulaciones=Count('id'),
        promedio_salario=Avg('pretension_salarial')
    ).order_by('-total_postulaciones')

    # Total general de postulaciones
    total_general = Postulacion.objects.count()

    return render(request, 'reporte_vacantes.html', {
        'reporte': reporte,
        'total_general': total_general
    })