from django.db import models
from django.contrib.auth.models import User
import secrets
import string

class Paciente(models.Model):
    nome = models.CharField(max_length=50)
    raca = models.CharField(max_length=50, default="N/A")
    idade = models.IntegerField(default=0)
    sexo = models.CharField(max_length=10, default="Indefinido")
    nome_tutor = models.CharField(max_length=50, null=True, blank=True)
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
    instituicao_pertencente = models.ForeignKey(
        "Instituicao", on_delete=models.CASCADE, null=True, blank=True
    )
    def __str__(self):
        return self.user.username


class Financeiro(models.Model):
    instituicao = models.ForeignKey(
        "Instituicao", on_delete=models.CASCADE, related_name="financeiros"
    )
    forma_pagamento = models.CharField(max_length=50, null=True, blank=True)
    clinica = models.ForeignKey("Clinica", on_delete=models.SET_NULL, null=True, blank=True)
    despesa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pago = models.BooleanField(default=False)
    data = models.DateTimeField(auto_now_add=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_repasse_a_clinica = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.instituicao} - {self.valor}"

    def lucro_liquido(self):
        return self.valor - self.despesa


class LancamentoFinanceiro(models.Model):
    data = models.DateField()
    paciente = models.CharField(max_length=255)
    tutor = models.CharField(max_length=255, blank=True)
    clinica = models.CharField(max_length=255, blank=True)
    tipo_exame = models.CharField(max_length=255, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField(max_length=100, blank=True)
    pago = models.BooleanField(default=False)
    enviado = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)


class Clinica(models.Model):
    nome_clinica = models.CharField(max_length=100, blank=True, null=True)
    whats_clinica = models.CharField(max_length=100, blank=True, null=True)
    usuario_logado = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.nome_clinica or "Clinica"


class VeterinarioPedidor(models.Model):
    nome = models.CharField(max_length=255)
    def __str__(self): return self.nome


class Exame(models.Model):
    codigo_acesso = models.CharField(max_length=255, null=True, blank=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    financeiro = models.ForeignKey(Financeiro, on_delete=models.CASCADE, null=True)
    modelo = models.ForeignKey("Modelo", on_delete=models.CASCADE, null=True)
    veterinario_pedidor = models.ForeignKey(VeterinarioPedidor, on_delete=models.CASCADE, null=True)
    PAPEL_ESCOLHAS_STATUS = [
        ("Laudado", "Laudado"),
        ("Aguardando", "Aguardando"),
        ("Urgente", "Urgente"),
    ]
    status = models.CharField(max_length=20, choices=PAPEL_ESCOLHAS_STATUS, default="Aguardando")
    subtipo_exame = models.CharField(max_length=100, null=True, blank=True)
    usuario_dicom = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="exames_dicom"
    )
    instituicao = models.ForeignKey(
        "Instituicao", on_delete=models.SET_NULL, null=True, blank=True, related_name="exames_instituicao"
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
    docx = models.FileField(
    upload_to="laudos_docx/",
    blank=True,
    null=True
    )
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
    usuario_logado = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        related_name="modelos", null=True, blank=True
    )
    nome_modelo = models.CharField(max_length=100)
    campo1  = models.TextField(blank=True)
    campo2  = models.TextField(blank=True)
    campo3  = models.TextField(blank=True)
    campo4  = models.TextField(blank=True)
    campo5  = models.TextField(blank=True)
    campo6  = models.TextField(blank=True)
    campo7  = models.TextField(blank=True)
    campo8  = models.TextField(blank=True)
    campo9  = models.TextField(blank=True)
    campo10 = models.TextField(blank=True)
    campo11 = models.TextField(blank=True)
    campo12 = models.TextField(blank=True)
    html_conteudo = models.TextField(blank=True, null=True)
    arquivo_docx = models.FileField(upload_to='modelos_docx/', null=True, blank=True)

    def __str__(self):
        return self.nome_modelo


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
        return sum(f.valor for f in self.financeiros.all() if f.pago)

    def a_receber(self):
        return sum(f.valor for f in self.financeiros.all() if not f.pago)