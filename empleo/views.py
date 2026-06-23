from django.shortcuts import render

# Create your views here.
def inicio(request):
    #Presentando en pantalla el contenido de inicio s
    return render(request, 'inicio.html')

def nuevoCandidato(request):
    return render(request, 'registrar_candidato.html')
