import json
from rest_framework import viewsets
from .models import Exame
from .serializers import ExameSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Usuario, Exame  # <-- aqui está o importante
from django.shortcuts import redirect
from base.services.orthanc_sync import sincronizar_estudos
from django.contrib.auth.decorators import login_required
from .util import gerar_codigo_unico
from django.shortcuts import render
from .models import Exame

@login_required
def sync_exames(request):

    sincronizar_estudos()

    return redirect("dashboard")

@csrf_exempt
def novo_exame(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Webhook recebido:", data)
            return JsonResponse({"status": "ok"})
        except Exception as e:
            print("Erro:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "invalid method"}, status=405)


@login_required
def dashboard(request):
    usuario, created = Usuario.objects.get_or_create(user=request.user)
    exames = Exame.objects.filter(usuario_veterinario=usuario)

    return render(request, "dashbord.html", {"exames": exames})    

def home(request):
    form = AuthenticationForm()
    return render(request, "home.html", {"form": form})

@login_required
def laudo_editor(request, exame_id):

    exame = Exame.objects.get(id=exame_id)

    # gera código apenas se não existir
    if not exame.codigo_acesso:

        exame.codigo_acesso = gerar_codigo_unico()
        exame.save()

    return render(request, "laudo_editor.html", {
        "exame": exame
    })

def login_view(request):

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect("dashboard")  # aqui vai pro dashboard

    else:
        form = AuthenticationForm()
        
    return render(request, "login.html", {"form": form})

def portal_exame(request, codigo=None):

    if codigo:

        exame = Exame.objects.filter(codigo_acesso=codigo).first()

        if exame:
            return render(request, "portal_exame.html", {
                "exame": exame
            })

        return render(request, "portal.html", {
            "erro": "Código não encontrado"
        })

    return render(request, "portal.html")
@csrf_exempt
def salvar_laudo(request):

    if request.method == "POST":

        data = json.loads(request.body)

        exame = Exame.objects.get(
            study_instance_uid=data["studyInstanceUid"]
        )

        exame.laudo_html = data["laudoHTML"]

        exame.save()

        return JsonResponse({
            "codigo": exame.codigo_acesso
        })