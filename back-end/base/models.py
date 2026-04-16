from django.db import models
from django.contrib.auth.models import User
import secrets
import string

class Paciente(models.Model):
    nome = models.CharField(max_length=50)
    raca = models.CharField(max_length=50, default="N/A")
    idade = models.IntegerField(default=0)
    sexo = models.CharField(max_length=10, default="Indefinido")
    nome_tutor= models.CharField(max_length=50,null=True,blank=True)
    def __str__(self):
        return self.nome


class Usuario(models.Model):
    PAPEL_ESCOLHAS = [
        ("V", "Veterinario"),
        ("T", "Tecnico"),
        ("A", "Administrador"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    papel = models.CharField(max_length=1, choices=PAPEL_ESCOLHAS)
    numero_celular = models.CharField(max_length=50, null=True, blank=True)
    instituicao_pertencente=models.ForeignKey("Instituicao",on_delete=models.CASCADE,null=True,blank=True,)
    def __str__(self):
        return self.user.username


class Exame(models.Model):
    codigo_acesso = models.CharField(max_length=255, null=True, blank=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    PAPEL_ESCOLHAS_STATUS = [
        ("Laudado", "Laudado"),
        ("Aguardando", "Aguardando"),
        ("Urgente", "Urgente"),
    ]
    status = models.CharField(max_length=20, choices=PAPEL_ESCOLHAS_STATUS, default="Aguardando")

    usuario_dicom = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exames_dicom"
    )
    instituicao = models.ForeignKey(
        "Instituicao",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exames_instituicao"
    )

    pdf = models.FileField(upload_to="laudos/", blank=True)
    laudo_html = models.TextField(blank=True, null=True)
    study_instance_uid = models.CharField(max_length=255, unique=True)
    accession_number = models.CharField(max_length=100, null=True, blank=True)
    study_date = models.DateField(null=True, blank=True)
    study_time = models.TimeField(null=True, blank=True)
    orthanc_ids = models.JSONField(default=list, blank=True)
    descricao = models.CharField(max_length=255, null=True, blank=True)
    medico_solicitante = models.CharField(max_length=255, null=True, blank=True)
    tipo_exame = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return self.study_instance_uid

    def save(self, *args, **kwargs):
        if not self.codigo_acesso:
            self.codigo_acesso = self._gerar_codigo()
        super().save(*args, **kwargs)

    def _gerar_codigo(self):
        chars = string.ascii_uppercase + string.digits
        while True:
            codigo = ''.join(secrets.choice(chars) for _ in range(6))
            if not Exame.objects.filter(codigo_acesso=codigo).exists():
                return codigo


class Laudo(models.Model):
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE)
    texto = models.TextField()
    data_finalizacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Laudo - {self.exame.study_instance_uid}"


class Modelo(models.Model):
    usuario_logado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="modelos")
    nome_modelo = models.CharField(max_length=100)
    campo2 = models.TextField(blank=True)
    campo3 = models.TextField(blank=True)
    campo4 = models.TextField(blank=True)
    campo5 = models.TextField(blank=True)
    campo6 = models.TextField(blank=True)
    campo7 = models.TextField(blank=True)
    campo8 = models.TextField(blank=True)
    campo9 = models.TextField(blank=True)
    campo10 = models.TextField(blank=True)
    campo11 = models.TextField(blank=True)
    campo12 = models.TextField(blank=True)


class Instituicao(models.Model):
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logo/', null=True, blank=True)
    cnpj = models.TextField(blank=True)
    membros_insituticao = models.ManyToManyField(Usuario, null=True, blank=True, related_name="instituicoes")
    exames = models.ManyToManyField("Exame", blank=True, related_name="instituicoes")

    def __str__(self):
        return self.nome
    def recebido(self):
        total = 0
        for f in self.financeiros.all():
            if f.pago:
                total += f.valor
        return total

    def a_receber(self):
        total = 0
        for f in self.financeiros.all():
            if not f.pago:
                total += f.valor
        return total


class Financeiro(models.Model):
    exame = models.ForeignKey("Exame", on_delete=models.CASCADE)

    instituicao = models.ForeignKey(
        "Instituicao",
        on_delete=models.CASCADE,
        related_name="financeiros"
    )

    clinica = models.ForeignKey("Clinica", on_delete=models.SET_NULL, null=True, blank=True)

    valor = models.DecimalField(max_digits=10, decimal_places=2)
    despesa = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    pago = models.BooleanField(default=False)

    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return {self.instituicao} - {self.valor}

def lucro_liquido(self):
    return self.entrada - self.despesa


class Clinica(models.Model):
    nome = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nome or "Clinica"