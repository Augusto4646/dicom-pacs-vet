from django.contrib import admin
from .models import Usuario, Instituicao, Exame, Paciente


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'papel']
    list_filter = ['papel']
    search_fields = ['user__username', 'user__email']


@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario_dicom', 'instituicao', 'paciente']


@admin.register(Instituicao)
class InstituicaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cidade']
    list_filter = ['cidade']
    search_fields = ['nome', 'cidade']


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'raca', 'idade']
    list_filter = ['raca']
    search_fields = ['nome', 'raca']
