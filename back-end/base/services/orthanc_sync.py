import requests  # type: ignore
from datetime import datetime
from base.models import Exame, Paciente, Clinica, Usuario
	
ORTHANC_URL = "http://vizionvet.com.br/orthanc"

def sincronizar_estudos():

    response = requests.get(f"{ORTHANC_URL}/studies")
    estudos = response.json()

    clinica = Clinica.objects.first()

    if not clinica:
        print("Nenhuma clínica cadastrada.")
        return
    dados_string = requests.get("http://vizionvet.com.br/orthanc/instances?expand&requested-tags=PatientName")
    dados_json = dados_string.json()

    lista_orthanc_instances = []

    for i in dados_json:
        lista_orthanc_instances.append({
            "nome": i["RequestedTags"]["PatientName"],
            "numero_instancia": i["MainDicomTags"]["InstanceNumber"],
            "index": i["IndexInSeries"],
            "id": i["ID"]
        })

    lista_final = {}

    for x in lista_orthanc_instances:
        lista_final[x["nome"]] = []

    for x in lista_orthanc_instances:
        lista_final[x["nome"]].append(x["id"])


    for estudo_id in estudos:

        detalhes = requests.get(f"{ORTHANC_URL}/studies/{estudo_id}").json()

        main_tags = detalhes.get("MainDicomTags", {})
        patient_tags = detalhes.get("PatientMainDicomTags", {})

        study_uid = main_tags.get("StudyInstanceUID")

        if not study_uid:
            continue

        # evitar duplicado
        if Exame.objects.filter(study_instance_uid=study_uid).exists():
            continue

        patient_name = patient_tags.get("PatientName", "Desconhecido")

        paciente, _ = Paciente.objects.get_or_create(
            nome=patient_name,
            clinica=clinica
        )

        nome_ref = main_tags.get("InstitutionName", "")
        
        # normaliza o nome do DICOM
        nome_ref = nome_ref.lower().strip().replace(" ", "-")

        print("Nome vindo do DICOM:", nome_ref)

        veterinario = Usuario.objects.filter(
            user__username__iexact=nome_ref
        ).first()

        print("Veterinario encontrado:", veterinario)

        # converter data/hora
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

        Exame.objects.create(
            paciente=paciente,
            usuario_veterinario=veterinario,
            study_instance_uid=study_uid,
            accession_number=main_tags.get("AccessionNumber"),
            study_date=parsed_date,
            study_time=parsed_time,
            descricao=main_tags.get("StudyDescription"),
            medico_solicitante=nome_ref,
            orthanc_ids=lista_final.get(patient_name, []),
            status="recebido"
        )

        print("Nome do DICOM:", nome_ref)
        print("Usuarios:", Usuario.objects.values_list("user__username", flat=True))
        print(f"Exame criado: {study_uid}")
