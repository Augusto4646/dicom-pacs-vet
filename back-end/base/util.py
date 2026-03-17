import secrets
from .models import Exame

def gerar_codigo_unico():

    while True:

        codigo = secrets.token_hex(3).upper()

        if not Exame.objects.filter(codigo_acesso=codigo).exists():
            return codigo