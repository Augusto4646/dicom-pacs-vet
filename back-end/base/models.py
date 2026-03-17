from django.db import models
from django.contrib.auth.models import User
import secrets
from django.db import models

class Clinica(models.Model): 
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logo/', null=True, blank=True)

    def __str__(self):
        return self.nome

class Paciente(models.Model):
    nome = models.CharField(max_length=50)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    raca = models.CharField(max_length=50, default="N/A")
    idade = models.IntegerField(default=0)
    sexo = models.CharField(max_length=10, default="Indefinido")
    
    def __str__(self):
        return self.nome



class Usuario(models.Model):
    PAPEL_ESCOLHAS = [
    ("V", "Veterinario"),
    ("T", "Tutor"),
    ("A", "Administrador"),
]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    papel = models.CharField(
        max_length=1,
        choices=PAPEL_ESCOLHAS
    )


    numero_celular = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username
class Exame(models.Model):

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    codigo_acesso = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        null=True
    )

    usuario_veterinario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exames_veterinario"
    )

    usuario_tutor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exames_tutor"
    )

    pdf = models.FileField(upload_to="laudos/", blank=True)

    study_instance_uid = models.CharField(max_length=255, unique=True)

    accession_number = models.CharField(max_length=100, null=True, blank=True)
    study_date = models.DateField(null=True, blank=True)
    study_time = models.TimeField(null=True, blank=True)

    descricao = models.CharField(max_length=255, null=True, blank=True)

    medico_solicitante = models.CharField(max_length=255, null=True, blank=True)

    instituicao = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=30, default="recebido")

    def __str__(self):
        return self.study_instance_uid



class Laudo(models.Model):
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE)
    texto = models.TextField()
    data_finalizacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Laudo - {self.exame.study_instance_uid}"