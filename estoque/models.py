from django.db import models
from datetime import date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import User

class Estabelecimento(models.Model):
    TIPOS_ESTABELECIMENTO = [
        ('Farmacia', 'Farmácia'),
        ('Almoxarifado Central', 'Almoxarifado Central'),
    ]

    nome = models.CharField(max_length=255)
    codigo_cnes = models.CharField(max_length=20)
    farmaceutico_responsavel = models.CharField(max_length=255)
    imagem_logotipo = models.ImageField(upload_to='logotipos/')
    tipo_estabelecimento = models.CharField(max_length=20, choices=TIPOS_ESTABELECIMENTO)

    def __str__(self):
        return self.nome

from django.contrib.auth.models import User
from .models import Estabelecimento 

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    estabelecimento = models.ForeignKey('Estabelecimento', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.estabelecimento if self.estabelecimento else "Sem Estabelecimento"}'
    
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

class EntradaEstoque(models.Model):
    TIPO_MOVIMENTACAO_CHOICES = (
        ("pregao", "Pregão"),
        ("ajuste_estoque", "Ajuste de Estoque"),
        ("doacao", "Doação"),
        ("entrada_ordinaria", "Entrada Ordinária"),
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

    TIPOS_DOCUMENTO = [
        ('Nota Fiscal', 'Nota Fiscal'),
        ('Nota Simples Remessa', 'Nota Simples Remessa'),
        ('Outro', 'Outro')
    ]
    
    estabelecimento = models.ForeignKey(Estabelecimento, on_delete=models.CASCADE, default=1)
    tipo = models.CharField(max_length=50, choices=TIPO_MOVIMENTACAO_CHOICES, verbose_name="Tipo de Entrada")
    data_hora = models.DateTimeField(auto_now_add=True)
    data = models.DateField(default=date.today, verbose_name="Data Nota Fiscal")
    data_recebimento = models.DateField(default=date.today)
    fonte_financiamento = models.CharField(max_length=50, choices=FONTE_FINANCIAMENTO_CHOICES, default="municipal")
    fornecedor_tipo = models.CharField(max_length=50, choices=FORNECEDOR_TIPO_CHOICES, default="distribuidora")
    fornecedor = models.ForeignKey('Fornecedor', on_delete=models.CASCADE, null=True)
    tipo_documento = models.CharField(
        max_length=50,
        choices=TIPOS_DOCUMENTO,  # Define as opções disponíveis
        default='Nota Fiscal'  # Define o valor padrão
    )
    numero_documento = models.CharField(max_length=50, verbose_name="Número do Documento")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Valor Total")
    observacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Observação")
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Substituir operador por user

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} de medicamentos"
    
     

class Estoque(models.Model):
    estabelecimento = models.ForeignKey(Estabelecimento, on_delete=models.CASCADE, related_name='estoques')
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, related_name='estoques_medicamento')  # Adicionando related_name
    quantidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.medicamento.nome} - {self.estabelecimento.nome} - {self.quantidade} unidades"


class DetalhesMedicamento(models.Model):
    
    estoque = models.ForeignKey(Estoque, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=0)
    validade = models.DateField(blank=True, null=True)
    lote = models.CharField(max_length=50, blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Valor Unitário")
    localizacao = models.ForeignKey(Localizacao, on_delete=models.SET_NULL, null=True, blank=True,verbose_name=u"Localização")
    fabricante = models.ForeignKey(Fabricante, on_delete=models.SET_NULL, null=True, blank=True)
    estabelecimento = models.ForeignKey('Estabelecimento', on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        existing_record = None  # Garante que a variável sempre tem um valor
    
        if not self.pk:  # Se for um novo registro
            existing_record = DetalhesMedicamento.objects.filter(
                medicamento=self.medicamento, 
                lote=self.lote,
                estabelecimento=self.estabelecimento  # Filtrando pelo mesmo estabelecimento
            ).first()
        
            if existing_record:
                # Atualizar a quantidade do registro existente
                existing_record.quantidade += self.quantidade
                existing_record.save()
                return
    
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.lote} - {self.medicamento.nome} - {self.quantidade}'

   
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
    medico = models.ForeignKey('Medico', on_delete=models.SET_NULL, null=True, blank=True,  verbose_name="Médico")
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

import uuid
from django.db import models, transaction
from django.db.models import F
from django.utils.timezone import now


    
  # Define automaticamente como o horário atual



class SaidaEstoque(models.Model):
    STATUS_CHOICES = (
        ("INICIAL", "Inicial"),
        ("ATENDIDO", "Atendido"),
    )

    # Usaremos um UUID para garantir que o numero_saida seja único e gerado automaticamente
    numero_saida = models.CharField(max_length=36, unique=True, blank=True)  # Aumentado para suportar o UUID
    user = models.CharField(max_length=100)
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    data_atendimento = models.DateTimeField(default=now)
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="INICIAL")
    medicamento = models.ForeignKey('Medicamento', on_delete=models.CASCADE)
    lote = models.ForeignKey('DetalhesMedicamento', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # Gerar o número de saída usando UUID, caso ainda não tenha sido gerado
        if not self.numero_saida:
            self.numero_saida = str(uuid.uuid4())  # Gera um UUID único
        super(SaidaEstoque, self).save(*args, **kwargs)

    def __str__(self):
        return f'Saída {self.numero_saida} - {self.medicamento.nome} - {self.departamento.nome}'


from django.db import models

class Distribuicao(models.Model):
    estabelecimento_origem = models.ForeignKey(
        'Estabelecimento', on_delete=models.CASCADE, related_name='distribuicoes_origem'
    )
    estabelecimento_destino = models.ForeignKey(
        'Estabelecimento', on_delete=models.CASCADE, related_name='distribuicoes_destino'
    )
    data_atendimento = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.estabelecimento_origem} -> {self.estabelecimento_destino} ({self.data_atendimento})'


class DistribuicaoMedicamento(models.Model):
    
    
    distribuicao = models.ForeignKey(Distribuicao, on_delete=models.CASCADE, related_name='medicamentos')
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    
    lote = models.ForeignKey(
        DetalhesMedicamento,
        on_delete=models.CASCADE,
        related_name='distribuicoes_por_lote'  # Nome único para o relacionamento reverso
    )
    validade = models.ForeignKey(
        
        DetalhesMedicamento,
        on_delete=models.CASCADE,
        related_name='distribuicoes_por_validade'  # Nome único para o relacionamento reverso
    )
    medicamento = models.ForeignKey('Medicamento', on_delete=models.CASCADE)
    lote = models.ForeignKey('DetalhesMedicamento', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
   
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Deduzir do estoque do estabelecimento de origem
        estoque_origem = Estoque.objects.get(
            estabelecimento=self.distribuicao.estabelecimento_origem,
            medicamento=self.medicamento
        )
        if estoque_origem.quantidade < self.quantidade:
            raise ValueError("Estoque insuficiente no estabelecimento de origem.")

        estoque_origem.quantidade -= self.quantidade
        estoque_origem.save()

        # Adicionar ao estoque do estabelecimento de destino
        estoque_destino, created = Estoque.objects.get_or_create(
            estabelecimento=self.distribuicao.estabelecimento_destino,
            medicamento=self.medicamento,
            defaults={'quantidade': 0}
        )
        estoque_destino.quantidade += self.quantidade
        estoque_destino.save()

from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Requisicao(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Aprovada', 'Aprovada'),
        ('Processando Transferência', 'Processando Transferência'),
        ('Transferida', 'Transferida'),
        ('Rejeitada', 'Rejeitada'),
    ]

    estabelecimento_origem = models.ForeignKey(
        "Estabelecimento", on_delete=models.CASCADE, related_name="requisicoes_origem"
    )
    estabelecimento_destino = models.ForeignKey(
        "Estabelecimento", on_delete=models.CASCADE, related_name="requisicoes_destino"
    )
    observacoes = models.CharField(max_length=255, blank=True, null=True, verbose_name="Observações")
    data_requisicao = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Pendente")
    data_aprovacao = models.DateField(null=True, blank=True)
    usuario_aprovador = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="requisicoes_aprovadas"
    )

    def aprovar(self, usuario):
        """Aprova a requisição para que o estabelecimento de destino possa selecionar os lotes."""
        if self.status != "Pendente":
            raise ValidationError("A requisição já foi processada.")

        self.status = "Aprovada"
        self.data_aprovacao = timezone.now()
        self.usuario_aprovador = usuario
        self.save()

    def rejeitar(self, usuario):
        """Rejeita a requisição e altera o status."""
        if self.status != "Pendente":
            raise ValidationError("A requisição já foi processada.")

        self.status = "Rejeitada"
        self.data_aprovacao = timezone.now()
        self.usuario_aprovador = usuario
        self.save()

    def processar_transferencia(self):
        """Muda o status da requisição para permitir que o destino selecione os lotes."""
        if self.status != "Aprovada":
            raise ValidationError("A requisição precisa estar aprovada antes de processar a transferência.")

        self.status = "Processando Transferência"
        self.save()

    def confirmar_transferencia(self):
    
    
        if self.status != "Processando Transferência":
            raise ValidationError("A requisição precisa estar em processamento para a transferência.")

        with transaction.atomic():
            for item in self.itens.all():
                item.transferir_estoque()  # Este método move os medicamentos entre os estoques
        
        self.status = "Transferida"
        self.save()

class ItemRequisicao(models.Model):
    requisicao = models.ForeignKey(Requisicao, related_name="itens", on_delete=models.CASCADE)
    medicamento = models.ForeignKey("Medicamento", on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    lote = models.ForeignKey("DetalhesMedicamento", null=True, blank=True, on_delete=models.SET_NULL)

    def transferir_estoque(self):
        """Realiza a transferência do estoque entre estabelecimentos."""

        if self.requisicao.status != "Processando Transferência":
            raise ValidationError("A requisição precisa estar em processamento para a transferência.")

        print(f"📌 REQUISIÇÃO #{self.requisicao.id}")
        print(f"📦 Medicamento: {self.medicamento}")
        print(f"🏥 Estabelecimento SOLICITANTE: {self.requisicao.estabelecimento_origem}")  # Posto Planalto
        print(f"🏭 Estabelecimento FORNECEDOR: {self.requisicao.estabelecimento_destino}")  # Almoxarifado Central
        print(f"🏥 Estabelecimento de origem: {self.requisicao.estabelecimento_origem}")


        estoque_origem_list = DetalhesMedicamento.objects.filter(
            estabelecimento=self.requisicao.estabelecimento_destino,  # Mudando para o fornecedor
            medicamento=self.medicamento
        ).order_by('validade')

        if not estoque_origem_list.exists():
            print(f"🚨 Nenhum lote encontrado no {self.requisicao.estabelecimento_origem} para {self.medicamento}")
            raise ValidationError("Erro: Nenhum lote encontrado no estoque de origem!")

        # Exibir os detalhes dos lotes encontrados
        print(f"📦 Estoque de origem encontrado: {list(estoque_origem_list.values('lote', 'quantidade', 'validade'))}")

        # Verifica o total disponível no estoque de origem
        quantidade_total_disponivel = sum(item.quantidade for item in estoque_origem_list)

        print(f"🔢 Quantidade disponível: {quantidade_total_disponivel} | Quantidade solicitada: {self.quantidade}")

        if quantidade_total_disponivel < self.quantidade:
            print("🚨 Erro: Estoque insuficiente na origem!")
            raise ValidationError("Estoque insuficiente na origem para a transferência.")

        # Distribuir a retirada entre os lotes disponíveis
        quantidade_a_transferir = self.quantidade

        for estoque_origem in estoque_origem_list:
            if quantidade_a_transferir == 0:
                break

            if estoque_origem.quantidade >= quantidade_a_transferir:
                estoque_origem.quantidade -= quantidade_a_transferir
                estoque_origem.save()
                quantidade_a_transferir = 0
            else:
                quantidade_a_transferir -= estoque_origem.quantidade
                estoque_origem.quantidade = 0
                estoque_origem.save()

        print(f"✅ Transferência concluída! Estoque de origem atualizado.")

        # Criar ou atualizar o estoque no DESTINO (para onde o medicamento vai)
        estoque_destino = DetalhesMedicamento.objects.filter(
            estabelecimento=self.requisicao.estabelecimento_destino,
            medicamento=self.medicamento
        ).first()

        if not estoque_destino:
            estoque_destino = DetalhesMedicamento.objects.create(
             estabelecimento=self.requisicao.estabelecimento_destino,
                medicamento=self.medicamento,
                quantidade=0,
                validade=estoque_origem_list.first().validade if estoque_origem_list else None,
                lote=estoque_origem_list.first().lote if estoque_origem_list else None,
                fabricante=estoque_origem_list.first().fabricante if estoque_origem_list else None
    )


        # Adiciona a quantidade transferida ao ESTOQUE DE DESTINO
        estoque_destino.quantidade += self.quantidade
        estoque_destino.save()

        print(f"✅ Transferência concluída! Novo estoque no destino: {estoque_destino.quantidade}")












