from django.core.management.base import BaseCommand
from base.services.orthanc_sync import sincronizar_estudos

class Command(BaseCommand):
    help = "Sincroniza estudos do Orthanc"

    def handle(self, *args, **kwargs):
        sincronizar_estudos()
        self.stdout.write(self.style.SUCCESS("Sincronização concluída"))