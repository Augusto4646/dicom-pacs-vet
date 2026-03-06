from rest_framework import serializers
from .models import Usuario, Clinica, Paciente, Exame, Laudo


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'


class ClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinica
        fields = '__all__'


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'


class ExameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exame
        fields = '__all__'


class LaudoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laudo
        fields = '__all__'
