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
from .models import Usuario, Exame,Modelo,Laudo,Paciente,Instituicao,Financeiro,Clinica,VeterinarioPedidor
from .serializers import ExameSerializer
from .util import gerar_codigo_unico
from base.services.orthanc_sync import sincronizar_estudos
import requests
from django.http import HttpResponse, Http404
from base.models import Exame
import io
import zipfile
import pydicom
import numpy as np
from PIL import Image
import io
import base64
from django.db.models import Sum

ORTHANC_URL = "http://vizionxvet.conexao46.com.br/orthanc"

# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------

@login_required
def sync_exames(request):
    sincronizar_estudos()
    return redirect("dashbord")


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
def dashbord(request):
    usuario, created = Usuario.objects.get_or_create(user=request.user)

    exames = Exame.objects.filter(
    instituicao__in=usuario.instituicoes.all()
    ).order_by('-id')

    return render(request, "dashbord.html", {"exames": exames})


@login_required
def menu(request):
    usuario, _ = Usuario.objects.get_or_create(user=request.user)
    inst = usuario.instituicao_pertencente
    exames = Exame.objects.filter(instituicao__in=usuario.instituicoes.all()).order_by('-id')

    financeiros = Financeiro.objects.filter(instituicao=inst)
    a_receber = financeiros.filter(pago=False).aggregate(t=Sum('valor'))['t'] or 0
    recebido  = financeiros.filter(pago=True).aggregate(t=Sum('valor'))['t'] or 0
    despesa   = financeiros.aggregate(t=Sum('despesa'))['t'] or 0
    saldo_liquido = recebido - despesa

    total_aguardando = exames.filter(status='Aguardando').count()
    total_urgente    = exames.filter(status='Urgente').count()
    total_laudado    = exames.filter(status='Laudado').count()
    clinicas_devedoras = (
    Financeiro.objects
    .filter(pago=False, clinica__isnull=False)
    .values('clinica__nome_clinica', 'clinica__id')
    .annotate(total=Sum('valor'))
    .order_by('-total')
    )

    return render(request, "menu.html", {
        "a_receber": a_receber,
        "recebido": recebido,
        "despesa": despesa,
        "saldo_liquido": saldo_liquido,
        "exames_recentes": exames[:5],
        "total_aguardando": total_aguardando,
        "total_urgente": total_urgente,
        "total_laudado": total_laudado,
        "total_exames": exames.count(),
        "clinicas_devedoras": clinicas_devedoras,

    })
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
            return redirect("menu")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})

def pagina_laudos(request):
 return render(request,"pagina_laudos.html",{"form":form})
# ---------------------------------------------------------------------------
# Editor de laudo
# ---------------------------------------------------------------------------

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

        ORTHANC_URL = "http://vizionxvet.conexao46.com.br/orthanc"
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

# ---------------------------------------------------------------------------
# Baixar todos dicons de um paciente
# ---------------------------------------------------------------------------

def baixar_dicom(request, exame_id):
    try:
        exame = Exame.objects.get(id=exame_id)
    except Exame.DoesNotExist:
        raise Http404("Exame não encontrado")

    if not exame.orthanc_ids:
        return HttpResponse("Sem DICOM disponível", status=400)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for i, orthanc_id in enumerate(exame.orthanc_ids):
            url = f"{ORTHANC_URL}/instances/{orthanc_id}/file"
            response = requests.get(url)
            if response.status_code == 200:
                zip_file.writestr(f"exame_{exame.id}_{i+1}.dcm", response.content)

    zip_buffer.seek(0)

    http_response = HttpResponse(zip_buffer, content_type="application/zip")
    http_response["Content-Disposition"] = f'attachment; filename="exame_{exame.id}.zip"'
    return http_response

# ---------------------------------------------------------------------------
# Transformar os dicom em imagens para a finalizaçao do laudo
# ---------------------------------------------------------------------------

def dicom_para_imagens(request, exame_id):
    exame = get_object_or_404(Exame, id=exame_id)
    imagens_base64 = []
    for orthanc_id in exame.orthanc_ids:
        response = requests.get(f"{ORTHANC_URL}/instances/{orthanc_id}/rendered")
        if response.status_code != 200:
            continue
        base64_img = base64.b64encode(response.content).decode("utf-8")
        imagens_base64.append(f"data:image/jpeg;base64,{base64_img}")
    return JsonResponse({"imagens": imagens_base64})
# ---------------------------------------------------------------------------
# Listar todos modelos de um usuario
# ---------------------------------------------------------------------------
def listar_modelos(request):
     usuario, created = Usuario.objects.get_or_create(user=request.user)

     modelos = Modelo.objects.filter(
        usuario_logado=usuario
     )
     return render(request, "pagina_modelos.html", {"modelos": modelos})
# ---------------------------------------------------------------------------
# Criar um novo modelo
# --------------------------------------------------------------------------
def criar_modelos(request):
    if request.method == "POST":
        usuario, created = Usuario.objects.get_or_create(user=request.user)
        Modelo.objects.create(
            usuario_logado=usuario,
            nome_modelo=request.POST.get("nome_modelo"),
            campo2=request.POST.get("campo2"),
            campo3=request.POST.get("campo3"),
            campo4=request.POST.get("campo4"),
            campo5=request.POST.get("campo5"),
            campo6=request.POST.get("campo6"),
            campo7=request.POST.get("campo7"),
            campo8=request.POST.get("campo8"),
            campo9=request.POST.get("campo9"),
            campo10=request.POST.get("campo10"),
            campo11=request.POST.get("campo11"),
            campo12=request.POST.get("campo12"),
        )
        modelos = Modelo.objects.filter(usuario_logado=usuario)
        return redirect('/listar_modelos/')

def deletar_modelo(request, modelo_id):
    modelo = get_object_or_404(Modelo, id=modelo_id)
    modelo.delete()
    return redirect('/listar_modelos/')

def listar_clinicas(request):
    usuario, _ = Usuario.objects.get_or_create(user=request.user)
    inst = usuario.instituicao_pertencente
    clinicas = Clinica.objects.all()
    return render(request, "pagina_clinicas.html", {"clinicas": clinicas})

 

def criar_clinica(request):
    if request.method == "POST":
        usuario, created = Usuario.objects.get_or_create(user=request.user)
        Clinica.objects.create(
            usuario_logado=usuario,
            nome_clinica=request.POST.get("nome_clinica"),
            whats_clinica=request.POST.get("whats_clinica"),
        )
        clinicas = Clinica.objects.filter(usuario_logado=usuario)
        return render(request, "pagina_clinicas.html", {"clinicas": clinicas})


def deletar_clinica(request, clinica_id):
    clinica = get_object_or_404(Clinica, id=clinica_id)
    clinica.delete()
    return redirect('/listar_clinicas/')

 


def editar_clinica(request, clinica_id):
    clinica = get_object_or_404(Clinica, id=clinica_id)
    if request.method == "POST":
        clinica.nome_clinica = request.POST.get("nome_clinica")
        clinica.whats_clinica = request.POST.get("whats_clinica")
        clinica.save()
        return redirect('/listar_clinicas/')
    return render(request, "editar_clinica.html", {"clinica": clinica})

@login_required
def laudo_editor(request, exame_id):
    usuario, created = Usuario.objects.get_or_create(user=request.user)
    exame = get_object_or_404(Exame, id=exame_id)
    exames = Exame.objects.filter(instituicao__in=usuario.instituicoes.all())
    membros = exame.instituicao.membros_insituticao.all() if exame.instituicao else []
    modelos = Modelo.objects.filter(usuario_logado=usuario)
    clinicas = Clinica.objects.filter(usuario_logado=usuario)
    vets = VeterinarioPedidor.objects.all()

    if request.method == 'POST':
        vet_id = request.POST.get("veterinario_pedidor")
        if vet_id:
            exame.veterinario_pedidor_id = vet_id

        exame.tipo_exame = request.POST.get("tipo_exame")
        if not exame.codigo_acesso:
            exame.codigo_acesso = exame._gerar_codigo()
        exame.save()

        exame.paciente.nome = request.POST.get("Paciente")
        exame.paciente.nome_tutor = request.POST.get("Tutor")
        exame.paciente.save()

        valor = request.POST.get("valor") or 0
        repasse = request.POST.get("repasse") or 0
        pago = request.POST.get("pago") == "on"
        forma = request.POST.get("forma_pagamento") or ""
        clinica_id = request.POST.get("clinica") or None

        if exame.financeiro:
            exame.financeiro.pago = pago
            exame.financeiro.valor = valor
            exame.financeiro.valor_repasse_a_clinica = repasse
            exame.financeiro.forma_pagamento = forma
            if clinica_id:
                exame.financeiro.clinica_id = clinica_id
            exame.financeiro.save()
        elif exame.instituicao:
            financeiro = Financeiro.objects.create(
                instituicao=exame.instituicao,
                pago=pago,
                valor=valor,
                valor_repasse_a_clinica=repasse,
                forma_pagamento=forma,
                clinica_id=clinica_id,
            )
            exame.financeiro = financeiro
            exame.save()

    return render(request, "laudo_editor.html", {
        "exame": exame,
        "exames": exames,
        "membros": membros,
        "modelos": modelos,
        "clinicas": clinicas,
        "veterinarios": vets,
    })# ---------------------------------------------------------------------------


def view_monitor(request, exame_id):
    usuario, created = Usuario.objects.get_or_create(user=request.user)
    exame = get_object_or_404(Exame, id=exame_id)
    exames = Exame.objects.filter(instituicao__in=usuario.instituicoes.all())
    membros = exame.instituicao.membros_insituticao.all() if exame.instituicao else []
    modelos = Modelo.objects.filter(usuario_logado=usuario)
    clinicas = Clinica.objects.filter(usuario_logado=usuario)
    vets = VeterinarioPedidor.objects.all()

    if request.method == 'POST':
        vet_id = request.POST.get("veterinario_pedidor")
        if vet_id:
            exame.veterinario_pedidor_id = vet_id

        exame.tipo_exame = request.POST.get("tipo_exame")
        if not exame.codigo_acesso:
            exame.codigo_acesso = exame._gerar_codigo()
        exame.save()

        exame.paciente.nome = request.POST.get("Paciente")
        exame.paciente.nome_tutor = request.POST.get("Tutor")
        exame.paciente.save()

        valor = request.POST.get("valor") or 0
        repasse = request.POST.get("repasse") or 0
        pago = request.POST.get("pago") == "on"
        forma = request.POST.get("forma_pagamento") or ""
        clinica_id = request.POST.get("clinica") or None

        if exame.financeiro:
            exame.financeiro.pago = pago
            exame.financeiro.valor = valor
            exame.financeiro.valor_repasse_a_clinica = repasse
            exame.financeiro.forma_pagamento = forma
            if clinica_id:
                exame.financeiro.clinica_id = clinica_id
            exame.financeiro.save()
        elif exame.instituicao:
            financeiro = Financeiro.objects.create(
                instituicao=exame.instituicao,
                pago=pago,
                valor=valor,
                valor_repasse_a_clinica=repasse,
                forma_pagamento=forma,
                clinica_id=clinica_id,
            )
            exame.financeiro = financeiro
            exame.save()

    return render(request, "lado_esquerdo.html", {
        "exame": exame,
        "exames": exames,
        "membros": membros,
        "modelos": modelos,
        "clinicas": clinicas,
        "veterinarios": vets,
    })# ---------------------------------------------------------------------------
# deletar modelo
# --------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Atualizar Status depois que move de tabela
# --------------------------------------------------------------------------
def atualizar_status(request, exame_id):
    if request.method == "POST":
        dados = json.loads(request.body)
        novo_status = dados['status']
        Exame.objects.filter(id=exame_id).update(status=novo_status)
        return JsonResponse({'ok': True})

def atualizar_status_laudo_editor(request, exame_id):
    if request.method == 'POST':
        Exame.objects.filter(id=exame_id).update(status="Laudado")
        return JsonResponse({'ok': True})
def dashboard_visual(request):
    exames = Exame.objects.all()

    colunas = [
        {"status": "Aguardando", "tema": "sunset", "titulo": "⏳ Aguardando"},
        {"status": "Urgente", "tema": "abyss", "titulo": "🚨 Urgente"},
        {"status": "Laudado", "tema": "forest", "titulo": "✅ Laudado"},
    ]

    return render(request, "dashbord.html", {
        "exames": exames,
        "colunas": colunas
    })


# ---------------------------------------------------------------------------
#EDITAR CABEÇALHO
# ---------------------------------------------------------------------------


def editar_cabecalho(request,exame_id):
    if request.method == "POST":#post pois modifica
        novo_nome = request.POST.get("novo_nome")#pega novo nome
        exame = get_object_or_404(Exame, id=exame_id)#retorna o exame compelto(nome,study_id codigo_acesso tudo daqquele exame daquele cara em espefico)

        for orthanc_id in exame.orthanc_ids:#percore todos orthanc_id daquele exame em espefico
         response = requests.post(f"{ORTHANC_URL}/instances/{orthanc_id}/modify",json={"Replace": {"PatientName":novo_nome},"Force":True})
        
    return JsonResponse({"status": "ok"})

def listar_veterinarios(request):
    vets = VeterinarioPedidor.objects.all()
    return render(request, "pagina_veterinarios.html", {"veterinarios": vets})

def criar_veterinario(request):
    if request.method == "POST":
        VeterinarioPedidor.objects.create(nome=request.POST.get("nome"))
        vets = VeterinarioPedidor.objects.all()
        return render(request, "pagina_veterinarios.html", {"veterinarios": vets})

def deletar_veterinario(request, veterinario_id):
    veterinario = get_object_or_404(VeterinarioPedidor, id=veterinario_id)
    veterinario.delete()  
    return redirect('/listar_veterinarios/')

def deletar_exame(request, exame_id):
    exame = get_object_or_404(Exame, id=exame_id)
    exame.delete()
    return redirect('/dashbord/')