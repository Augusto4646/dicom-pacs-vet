import requests
from datetime import datetime
from base.models import Exame, Paciente, Instituicao, Usuario
import re
import unicodedata

ORTHANC_URL = "http://vizionvet.com.br/orthanc"


def normalizar_nome(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    texto = re.sub(r"-+", "-", texto)
    return texto.strip("-")


def sincronizar_estudos():

    response = requests.get(f"{ORTHANC_URL}/studies")
    estudos = response.json()

    dados_string = requests.get(
        f"{ORTHANC_URL}/instances?expand&requested-tags=PatientName"
    )
    dados_json = dados_string.json()

    lista_orthanc_instances = []

    for i in dados_json:
        lista_orthanc_instances.append({
            "nome": i["RequestedTags"]["PatientName"],
            "id": i["ID"]
        })

    lista_final = {}

    for x in lista_orthanc_instances:
        lista_final.setdefault(x["nome"], []).append(x["id"])

    for estudo_id in estudos:

        detalhes = requests.get(f"{ORTHANC_URL}/studies/{estudo_id}").json()
        
        main_tags = detalhes.get("MainDicomTags", {})
        patient_tags = detalhes.get("PatientMainDicomTags", {})

        study_uid = main_tags.get("StudyInstanceUID")

        if not study_uid:
            continue

        if Exame.objects.filter(study_instance_uid=study_uid).exists():
            continue

        patient_name = patient_tags.get("PatientName", "Desconhecido")

        paciente, _ = Paciente.objects.get_or_create(nome=patient_name)

        nome_bruto = main_tags.get("InstitutionName", "")
        nome_ref = normalizar_nome(nome_bruto)

        print("DICOM bruto:", nome_bruto)
        print("Normalizado:", nome_ref)

        veterinario = Usuario.objects.filter(
            user__username__iexact=nome_ref
        ).first()

        print("Veterinario encontrado:", veterinario)

        instituicao = Instituicao.objects.filter(
            membros_insituticao=veterinario
        ).first()

        print("Instituicao encontrada:", instituicao)

        study_date = main_tags.get("StudyDate")
        study_time = main_tags.get("StudyTime")

        parsed_date = None
        parsed_time = None

        try:
            if study_date:
                parsed_date = datetime.strptime(study_date, "%Y%m%d").date()
            if study_time:
                parsed_time = datetime.strptime(study_time[:6], "%H%M%S").time()
        except:
            pass

        exame_criado = Exame.objects.create(
            paciente=paciente,
            usuario_dicom=veterinario,
            study_instance_uid=study_uid,
            accession_number=main_tags.get("AccessionNumber"),
            study_date=parsed_date,
            study_time=parsed_time,
            descricao=main_tags.get("StudyDescription"),
            medico_solicitante=nome_ref,
            orthanc_ids=lista_final.get(patient_name, []),
            status="Aguardando",
            instituicao=instituicao
        )

        if instituicao:
            instituicao.exames.add(exame_criado)

        print("Usuarios:", list(Usuario.objects.values_list("user__username", flat=True)))
        print(f"Exame criado: {study_uid}")