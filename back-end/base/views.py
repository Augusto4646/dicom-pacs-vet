import json
from rest_framework import viewsets
from .models import Exame
from .serializers import ExameSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


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