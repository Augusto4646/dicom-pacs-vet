import requests#type: ignore
from datetime import datetime
from base.models import Exame, Paciente, Clinica

ORTHANC_URL = "http://orthanc:8042"


def sincronizar_estudos():
    response = requests.get(f"{ORTHANC_URL}/studies")
    estudos = response.json()

    clinica = Clinica.objects.first()

    if not clinica:
        print("Nenhuma clínica cadastrada.")
        return

    for estudo_id in estudos:
        detalhes = requests.get(f"{ORTHANC_URL}/studies/{estudo_id}").json()

        main_tags = detalhes.get("MainDicomTags", {})
        patient_tags = detalhes.get("PatientMainDicomTags", {})

        study_uid = main_tags.get("StudyInstanceUID")

        if not study_uid:
            continue

        # Se já existe no banco, ignora
        if Exame.objects.filter(study_instance_uid=study_uid).exists():
            continue

        patient_name = patient_tags.get("PatientName", "Desconhecido")

        paciente, _ = Paciente.objects.get_or_create(
            nome=patient_name,
            clinica=clinica
        )

        # Converter data e hora DICOM
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
            clinica=clinica,
            paciente=paciente,
            study_instance_uid=study_uid,
            accession_number=main_tags.get("AccessionNumber"),
            study_date=parsed_date,
            study_time=parsed_time,
            descricao=main_tags.get("StudyDescription"),
            medico_solicitante=main_tags.get("ReferringPhysicianName"),
            instituicao=main_tags.get("InstitutionName"),
            status="recebido"
        )

        print(f"Exame criado: {study_uid}")