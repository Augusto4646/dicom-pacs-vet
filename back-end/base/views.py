import json
import base64
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from rest_framework import viewsets
from .models import Usuario, Exame
from .serializers import ExameSerializer
from .util import gerar_codigo_unico
from base.services.orthanc_sync import sincronizar_estudos
import requests
from django.http import HttpResponse, Http404
from base.models import Exame

ORTHANC_URL = "http://vizionvet.com.br/orthanc"

# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------

@login_required
def sync_exames(request):
    sincronizar_estudos()
    return redirect("dashboard")


# ---------------------------------------------------------------------------
# Webhook — recebe novo exame do Orthanc
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    usuario, created = Usuario.objects.get_or_create(user=request.user)

    exames = Exame.objects.filter(
        usuario_veterinario=usuario
    ).order_by('-study_date')

    return render(request, "dashbord.html", {"exames": exames})


# ---------------------------------------------------------------------------
# Home / Login
# ---------------------------------------------------------------------------

def home(request):
    form = AuthenticationForm()
    return render(request, "home.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


# ---------------------------------------------------------------------------
# Editor de laudo
# ---------------------------------------------------------------------------

@login_required
def laudo_editor(request, exame_id):
    exame = get_object_or_404(Exame, id=exame_id)
    exames = Exame.objects.filter(usuario_veterinario=exame.usuario_veterinario)
    # Gera código de acesso apenas se ainda não existir
    if not exame.codigo_acesso:
        exame.codigo_acesso = gerar_codigo_unico()
        exame.save()

    return render(request, "laudo_editor.html", {"exame": exame, "exames": exames})

# ---------------------------------------------------------------------------
# Salvar laudo (HTML)
# ---------------------------------------------------------------------------

@login_required
@csrf_exempt
def salvar_laudo(request):
    if request.method == "POST":
        data = json.loads(request.body)

        exame = get_object_or_404(
            Exame,
            study_instance_uid=data["studyInstanceUid"]
        )

        exame.laudo_html = data["laudoHTML"]
        exame.save()

        return JsonResponse({"codigo": exame.codigo_acesso})

    return JsonResponse({"error": "invalid method"}, status=405)


# ---------------------------------------------------------------------------
# Salvar PDF — recebe base64 do frontend e salva no FileField do banco
# ---------------------------------------------------------------------------

@login_required
@csrf_exempt
def salvar_pdf(request, exame_id):
    if request.method == "POST":
        exame = get_object_or_404(Exame, id=exame_id)

        data = request.POST.get("pdf_base64")

        if not data:
            return JsonResponse({"error": "pdf_base64 ausente"}, status=400)

        # Remove o prefixo "data:application/pdf;base64,"
        format, imgstr = data.split(";base64,")
        pdf_bytes = base64.b64decode(imgstr)

        # Salva no campo laudo_pdf do modelo
        exame.pdf.save(
            f"laudo_{exame.id}.pdf",
            ContentFile(pdf_bytes),
            save=True  # já chama exame.save()
        )

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "invalid method"}, status=405)


# ---------------------------------------------------------------------------
# Upload de PDF via formulário (alternativa ao base64)
# ---------------------------------------------------------------------------

@login_required
def upload_laudo_pdf(request):
    if request.method == "POST":
        exame_id = request.POST.get("exame_id")
        pdf = request.FILES.get("pdf")

        exame = get_object_or_404(Exame, id=exame_id)
        exame.laudo_pdf.save(f"laudo_{exame.id}.pdf", pdf)

        return JsonResponse({"ok": True})

    return JsonResponse({"error": "invalid method"}, status=405)


# ---------------------------------------------------------------------------
# Portal do paciente — acessa o laudo pelo código
# ---------------------------------------------------------------------------

def portal_exame(request, codigo=None):
    if codigo:
        exame = Exame.objects.filter(codigo_acesso=codigo).first()

        if exame:
            return render(request, "portal_exame.html", {"exame": exame})

        return render(request, "portal.html", {"erro": "Código não encontrado"})

    return render(request, "portal.html")


# ---------------------------------------------------------------------------
# Editar nome do paciente (atualiza banco + Orthanc)
# ---------------------------------------------------------------------------

@login_required
def editar_paciente(request, exame_id):
    if request.method == "POST":
        novo_nome = request.POST.get("nome")
        exame = get_object_or_404(Exame, id=exame_id)

        ORTHANC_URL = "http://vizionvet.com.br/orthanc"
        study_uid = exame.study_instance_uid

        find = requests.post(
            f"{ORTHANC_URL}/tools/find",
            json={
                "Level": "Study",
                "Query": {"StudyInstanceUID": study_uid}
            }
        ).json()

        if not find:
            return JsonResponse({"erro": "Estudo não encontrado no Orthanc"})

        study_id = find[0]

        requests.post(
            f"{ORTHANC_URL}/studies/{study_id}/modify",
            json={
                "Replace": {"PatientName": novo_nome},
                "KeepSource": False
            }
        )

        exame.paciente.nome = novo_nome
        exame.paciente.save()

        return JsonResponse({"ok": True})

    return JsonResponse({"error": "invalid method"}, status=405)


def baixar_dicom(request, exame_id):

    try:
        exame = Exame.objects.get(id=exame_id)
    except Exame.DoesNotExist:
        raise Http404("Exame não encontrado")

    if not exame.orthanc_instance_id:
        return HttpResponse("Sem DICOM disponível", status=400)

    # 🔥 chamada ao Orthanc
    url = f"{ORTHANC_URL}/instances/{exame.orthanc_instance_id}/file"

    response = requests.get(url)

    if response.status_code != 200:
        return HttpResponse("Erro ao buscar DICOM", status=500)

    # 🔥 retorno do arquivo
    http_response = HttpResponse(
        response.content,
        content_type="application/dicom"
    )

    http_response["Content-Disposition"] = f'attachment; filename="exame_{exame.id}.dcm"'

    return http_response
def forcar_codigos(request):
    exames = Exame.objects.filter(codigo_acesso__isnull=True)
    for exame in exames:
        exame.save()  # dispara o save() que gera o código
    return JsonResponse({"atualizados": exames.count()})

