from django.contrib import admin
from .models import Usuario, Clinica, Exame,Paciente

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'papel', 'clinica']
    list_filter = ['papel', 'clinica']
    search_fields = ['nome', 'username', 'gmail']


@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    list_display = ['id', 'clinica', 'usuario_veterinario', 'usuario_tutor', 'paciente']
    list_filter = ['clinica']

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display=['nome','cidade']
    list_filter=['nome','cidade']
    search_fields=['nome','cidade']

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display=['nome','raca','idade']
    list_filter=['nome','raca','idade']
    search_fields=['nome','raca','idade']
