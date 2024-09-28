from django.db import models
from datetime import date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import User
from .estabelecimento import Estabelecimento


class Departamento(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Localizacao(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Descrição da Localização")

    def __str__(self):
        return self.nome

class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    nome_mae = models.CharField(max_length=100, verbose_name="Nome da mãe")
    cns = models.CharField(max_length=15, unique=True, verbose_name="CNS")
    cpf = models.CharField(max_length=11, unique=True, verbose_name="CPF")
    data_nascimento = models.DateField()

    def __str__(self):
        return self.nome

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    nome_fantasia = models.CharField(max_length=100, blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome

class Fabricante(models.Model):
    nome = models.CharField(max_length=100)
    nome_fantasia = models.CharField(max_length=100, blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")

    def __str__(self):
        return self.nome

class Medicamento(models.Model):
    LISTA_CHOICES = [
        ('A', 'Lista A'),
        ('B', 'Lista B'),
        ('C', 'Lista C'),
    ]

    codigo_identificacao = models.CharField(max_length=100, blank=True, null=True)
    nome = models.CharField(max_length=255, blank=True, null=True)
    psicotropico = models.CharField(max_length=1, choices=LISTA_CHOICES, blank=True, null=True, verbose_name="Psicotrópico")

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        super(Medicamento, self).save(*args, **kwargs)

class Estoque(models.Model):
    TIPO_MOVIMENTACAO_CHOICES = (
        ("ajuste_estoque", "Ajuste de Estoque"),
        ("doacao", "Doação"),
        ("entrada_ordinaria", "Entrada Ordinária"),
        ("pregao", "Pregão"),
        ("saldo_implantacao", "Saldo de Implantação"),
    )

    FONTE_FINANCIAMENTO_CHOICES = (
        ("municipal", "Municipal"),
        ("federal", "Federal"),
        ("estadual_federal", "Estadual + Federal"),
    )

    FORNECEDOR_TIPO_CHOICES = (
        ("distribuidora", "Distribuidora"),
        ("entidade", "Entidade"),
    )

    tipo = models.CharField(max_length=50, choices=TIPO_MOVIMENTACAO_CHOICES, verbose_name="Tipo de Entrada")
    data_hora = models.DateTimeField(auto_now_add=True)
    data = models.DateField(default=date.today, verbose_name="Data Nota Fiscal")
    data_recebimento = models.DateField(default=date.today)
    fonte_financiamento = models.CharField(max_length=50, choices=FONTE_FINANCIAMENTO_CHOICES, default="municipal")
    fornecedor_tipo = models.CharField(max_length=50, choices=FORNECEDOR_TIPO_CHOICES, default="distribuidora")
    fornecedor = models.ForeignKey('Fornecedor', on_delete=models.CASCADE, null=True)
    tipo_documento = models.CharField(max_length=50, default="Nota Fiscal")
    numero_documento = models.CharField(max_length=50, default="0000", verbose_name="Número do Documento")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    observacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Observação")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} de medicamentos"

class DetalhesMedicamento(models.Model):
    estoque = models.ForeignKey(Estoque, on_delete=models.CASCADE, related_name='detalhes_medicamentos')
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=0)
    localizacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Localização")
    validade = models.DateField(blank=True, null=True)
    lote = models.CharField(max_length=50, blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Valor Unitário")
    fabricante = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.medicamento.nome} - {self.quantidade}'

class SaidaEstoque(models.Model):
    STATUS_CHOICES = (
        ("INICIAL", "Inicial"),
        ("ATENDIDO", "Atendido"),
    )

    numero_saida = models.CharField(max_length=8, unique=True)
    operador = models.CharField(max_length=100)  
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    data_atendimento = models.DateField()
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="INICIAL")
    medicamento = models.ForeignKey('Medicamento', on_delete=models.CASCADE)
    lote = models.CharField(max_length=50)
    quantidade = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if not self.numero_saida:
            self.numero_saida = self.generate_numero_saida()
        super().save(*args, **kwargs)

    def generate_numero_saida(self):
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(8)])

    def __str__(self):
        return f'Saída {self.numero_saida} - {self.medicamento.nome} - {self.departamento.nome}'

class Funcionalidade(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class PerfilOperador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    estabelecimentos = models.ManyToManyField(Estabelecimento, related_name='operadores')
    funcionalidades = models.ManyToManyField(Funcionalidade, related_name='perfis')

    def __str__(self):
        return self.user.username

class Operador(AbstractUser):
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    perfil = models.ForeignKey(PerfilOperador, on_delete=models.CASCADE)
    estabelecimentos = models.ManyToManyField(Estabelecimento)
    
    # Adicionando related_name para evitar conflito
    groups = models.ManyToManyField(
        Group,
        related_name='operador_set',  # ou outro nome que você preferir
        blank=True,
        help_text="Os grupos aos quais este usuário pertence."
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='operador_permissions_set',  # ou outro nome que você preferir
        blank=True,
        help_text="Permissões específicas para este usuário."
    )

    username = models.CharField(max_length=150, unique=True, default='default_username')
    # Definindo um valor padrão para 'password'
    password = models.CharField(max_length=128, default='senha_padrao')

    def __str__(self):
        return self.nome_completo

    def has_permission(self, funcionalidade_nome):
        return self.perfil.funcionalidades.filter(nome=funcionalidade_nome).exists()

class Medico(models.Model):
    ESTADOS_CHOICES = [
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ]

    nome_completo = models.CharField(max_length=255)
    estado = models.CharField(max_length=2, choices=ESTADOS_CHOICES)
    crm = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nome_completo

    def clean(self):
        # Ensure CRM is unique
        if Medico.objects.filter(crm=self.crm).exists():
            raise ValidationError('CRM já existe.')

    def save(self, *args, **kwargs):
        self.clean()
        super(Medico, self).save(*args, **kwargs)

class Dispensacao(models.Model):
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    medico = models.ForeignKey('Medico', on_delete=models.SET_NULL, null=True, blank=True)
    outros_prescritores = models.CharField(max_length=255, blank=True, null=True)
    numero_notificacao = models.CharField(max_length=6, blank=True, null=True, verbose_name="Número notificação")
    data_receita = models.DateField(default=timezone.now)
    data_dispensacao = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Dispensação para {self.paciente.nome} em {self.data_dispensacao}"

class DispensacaoMedicamento(models.Model):
    dispensacao = models.ForeignKey('Dispensacao', related_name='medicamentos', on_delete=models.CASCADE)
    medicamento = models.ForeignKey('Medicamento', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        detalhe_medicamentos = DetalhesMedicamento.objects.filter(medicamento=self.medicamento).order_by('validade')
        quantidade_a_subtrair = self.quantidade

        for detalhe_medicamento in detalhe_medicamentos:
            if detalhe_medicamento.quantidade >= quantidade_a_subtrair:
                detalhe_medicamento.quantidade -= quantidade_a_subtrair
                detalhe_medicamento.save()
                break
            else:
                quantidade_a_subtrair -= detalhe_medicamento.quantidade
                detalhe_medicamento.quantidade = 0
                detalhe_medicamento.save()

        super().save(*args, **kwargs)

class DetalheDispensacao(models.Model):
    dispensacao = models.ForeignKey('Dispensacao', related_name='detalhes', on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()



