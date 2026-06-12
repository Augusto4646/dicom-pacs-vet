import os
import requests
from django.conf import settings

ORTHANC_BASE = "https://pacsvisionxvet.conexao46.com.br/orthanc"


def get_orthanc_study_id(study_instance_uid: str) -> str | None:
    """Busca o ID interno do Orthanc pelo StudyInstanceUID via /tools/find."""
    try:
        resp = requests.post(
            f"{ORTHANC_BASE}/tools/find",
            json={"Level": "Study", "Query": {"StudyInstanceUID": study_instance_uid}},
            timeout=10
        )
        resp.raise_for_status()
        results = resp.json()
        return results[0] if results else None
    except Exception as e:
        print(f"[dicom_utils] Erro no tools/find: {e}")
        return None


def get_jpg_paths_for_study(study_instance_uid: str) -> list[str]:
    orthanc_study_id = get_orthanc_study_id(study_instance_uid)
    if not orthanc_study_id:
        return []

    cache_dir = os.path.join(settings.MEDIA_ROOT, "dicom_jpgs", orthanc_study_id)
    os.makedirs(cache_dir, exist_ok=True)
    print("study_instance_uid recebido =", study_instance_uid)
    print("orthanc_study_id encontrado =", orthanc_study_id)

    existing = sorted([
        os.path.join(cache_dir, f)
        for f in os.listdir(cache_dir) if f.endswith(".jpg")
    ])
    if existing:
        return existing

    try:
        resp = requests.get(f"{ORTHANC_BASE}/studies/{orthanc_study_id}/instances", timeout=15)
        resp.raise_for_status()
        instances = resp.json()
    except Exception as e:
        print(f"[dicom_utils] Erro ao buscar instâncias: {e}")
        return []

    paths = []
    for idx, instance in enumerate(instances):
        instance_id = instance.get("ID") or instance.get("id")
        if not instance_id:
            continue
        jpg_path = os.path.join(cache_dir, f"{idx:04d}.jpg")
        try:
            img_resp = requests.get(f"{ORTHANC_BASE}/instances/{instance_id}/preview", timeout=20)
            img_resp.raise_for_status()
            with open(jpg_path, "wb") as f:
                f.write(img_resp.content)
            paths.append(jpg_path)
        except Exception as e:
            print(f"[dicom_utils] Erro ao baixar instância {instance_id}: {e}")

    return sorted(paths)


def get_jpg_urls_for_study(study_instance_uid: str, request=None) -> list[str]:
    paths = get_jpg_paths_for_study(study_instance_uid)
    urls = []
    for path in paths:
        relative = os.path.relpath(path, settings.MEDIA_ROOT).replace(os.sep, "/")
        urls.append(settings.MEDIA_URL + relative)
    return urls