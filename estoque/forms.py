from django.forms import inlineformset_factory
from datetime import date
from django import forms
from .models import (
    Medicamento,
    EntradaEstoque,
    Paciente,
    Fornecedor,
    DetalhesMedicamento,
    Fabricante,
    Localizacao,
    Estabelecimento,
    Departamento,
    SaidaEstoque,
    DetalheDispensacao,
    Medico,
    Dispensacao,
    DispensacaoMedicamento,
   
)

from django.forms import modelformset_factory
from django.db.models import signals
from django import forms
from django.forms import formset_factory

from django import forms
from .models import Medicamento, DetalhesMedicamento

class MedicamentoForm(forms.ModelForm):
    lote = forms.ModelChoiceField(
        queryset=DetalhesMedicamento.objects.none(),
        required=False,
        label="Lote",
        help_text="Selecione o lote disponível para o medicamento."
    )

    class Meta:
        model = Medicamento
        fields = ['codigo_identificacao', 'nome', 'psicotropico', 'lote']

    def __init__(self, *args, **kwargs):
        estabelecimento_logado = kwargs.pop('estabelecimento_logado', None)
        super().__init__(*args, **kwargs)

        # Define choices para campo psicotrópico
        self.fields['psicotropico'].widget = forms.Select(choices=self.Meta.model.LISTA_CHOICES)

        # Filtra medicamentos por estabelecimento, se aplicável
        if estabelecimento_logado:
            self.fields['codigo_identificacao'].queryset = Medicamento.objects.filter(
                detalhesmedicamento__estabelecimento=estabelecimento_logado
            ).distinct()

        # Inicializa lotes vazios, atualizando se medicamento já foi selecionado
        if 'codigo_identificacao' in self.data:
            try:
                medicamento_id = int(self.data.get('codigo_identificacao'))
                self.fields['lote'].queryset = DetalhesMedicamento.objects.filter(
                    medicamento_id=medicamento_id,
                    estabelecimento=estabelecimento_logado,
                    quantidade__gt=0
                )
            except (ValueError, TypeError):
                pass


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ["nome", "nome_mae", "cns", "cpf", "data_nascimento"]

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ["nome", "nome_fantasia", "cnpj", "telefone"]

class FabricanteForm(forms.ModelForm):
    class Meta:
        model = Fabricante
        fields = ["nome", "nome_fantasia", "cnpj",]

class LocalizacaoForm(forms.ModelForm):
    class Meta:
        model = Localizacao
        fields = ["nome"]

class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ["nome"]

class LoginForm(forms.Form):
    
    operador = forms.CharField(max_length=100)
    senha = forms.CharField(widget=forms.PasswordInput)
    
from django import forms
from .models import EntradaEstoque

class EntradaEstoqueForm(forms.ModelForm):
    class Meta:
        model = EntradaEstoque
        fields = ['tipo', 'data', 'data_recebimento', 'fornecedor', 'tipo_documento', 'numero_documento', 'valor_total', 'observacao']


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retira 'user' de kwargs
        super().__init__(*args, **kwargs)
        
        if user and user.profile.estabelecimento:
            self.instance.estabelecimento = user.profile.estabelecimento


from django import forms
from .models import DetalhesMedicamento, Estoque, Medicamento, Fabricante, Localizacao
from django.forms import modelformset_factory

# Formulário para DetalhesMedicamento
class DetalhesMedicamentoForm(forms.ModelForm):
    medicamento = forms.ModelChoiceField(
        queryset=Medicamento.objects.all(),
        required=True,
        label="Medicamento"
    )
    fabricante = forms.ModelChoiceField(
        queryset=Fabricante.objects.all(),
        required=True,
        label="Fabricante"
    )
    localizacao = forms.ModelChoiceField(
        queryset=Localizacao.objects.all(),
        required=True,
        label="Localização"
    )

    class Meta:
        model = DetalhesMedicamento
        fields = ['medicamento', 'quantidade', 'localizacao', 'validade', 'lote', 'valor', 'fabricante']
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-control select2'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'lote': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'localizacao': forms.Select(attrs={'class': 'form-control select2'}),
            'fabricante': forms.Select(attrs={'class': 'form-control select2'})
        }

# FormSet para DetalhesMedicamento
DetalhesMedicamentoFormSet = modelformset_factory(
    DetalhesMedicamento,
    fields=('medicamento', 'quantidade', 'localizacao', 'validade', 'lote', 'valor', 'fabricante'),
    extra=1,  # Garante que pelo menos um formulário vazio apareça
    can_delete=True  # Habilita exclusão de itens no FormSet
)

class EstabelecimentoForm(forms.ModelForm):
    class Meta:
        model = Estabelecimento
        fields = ['nome', 'codigo_cnes', 'farmaceutico_responsavel', 'imagem_logotipo', 'tipo_estabelecimento']


      
class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['nome_completo', 'estado', 'crm']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome completo'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'crm': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CRM'}),
        }

class DispensacaoForm(forms.ModelForm):
    class Meta:
        model = Dispensacao
        fields = ['paciente', 'medico', 'outros_prescritores', 'numero_notificacao', 'data_receita']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'medico': forms.Select(attrs={'class': 'form-control'}),
            'outros_prescritores': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_notificacao': forms.TextInput(attrs={'class': 'form-control'}),
            'data_receita': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class DispensacaoMedicamentoForm(forms.ModelForm):
    class Meta:
        model = DispensacaoMedicamento
        fields = ['medicamento', 'quantidade']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar medicamentos com estoque disponível
        medicamentos_com_estoque = Medicamento.objects.filter(detalhesmedicamento__quantidade__gt=0).distinct()
        self.fields['medicamento'].queryset = medicamentos_com_estoque

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        medicamento = self.cleaned_data.get('medicamento')
        detalhe_medicamento = DetalhesMedicamento.objects.filter(medicamento=medicamento).order_by('validade').first()

        if detalhe_medicamento and detalhe_medicamento.quantidade < quantidade:
            raise forms.ValidationError(f'Estoque insuficiente. Quantidade disponível: {detalhe_medicamento.quantidade}.')

        return quantidade


DispensacaoMedicamentoFormSet = forms.inlineformset_factory(
    Dispensacao, DispensacaoMedicamento, form=DispensacaoMedicamentoForm, extra=1, can_delete=True
)


class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label='Selecione um arquivo Excel')




from django import forms
from .models import Requisicao, ItemRequisicao, Medicamento, Estabelecimento

class RequisicaoForm(forms.ModelForm):
    class Meta:
        model = Requisicao
        fields = ['estabelecimento_origem', 'estabelecimento_destino', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'maxlength': 100}),
        }

class ItemRequisicaoForm(forms.ModelForm):
    class Meta:
        model = ItemRequisicao
        fields = ['medicamento', 'quantidade']

    def __init__(self, *args, **kwargs):
        estabelecimento_destino = kwargs.pop('estabelecimento_destino', None)
        super().__init__(*args, **kwargs)
        if estabelecimento_destino:
            self.fields['medicamento'].queryset = Medicamento.objects.filter(estoque__estabelecimento=estabelecimento_destino)




from django import forms
from .models import SaidaEstoque, DetalhesMedicamento, Medicamento, Estoque

class SaidaEstoqueForm(forms.ModelForm):
    class Meta:
        model = SaidaEstoque
        fields = ['medicamento', 'lote', 'quantidade', 'departamento', 'observacao']
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-control', 'id': 'id_medicamento'}),
            'lote': forms.Select(attrs={'class': 'form-control', 'id': 'id_lote'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            estabelecimento = user.profile.estabelecimento
            self.fields['medicamento'].queryset = Medicamento.objects.filter(
            estoques_medicamento__estabelecimento=user.profile.estabelecimento
            ).distinct()


        # Se o medicamento já está selecionado, carregue os lotes correspondentes
        if 'medicamento' in self.data:
            try:
                medicamento_id = int(self.data.get('medicamento'))
                self.fields['lote'].queryset = DetalhesMedicamento.objects.filter(
                    medicamento_id=medicamento_id,
                    estabelecimento=estabelecimento,
                )
            except (ValueError, TypeError):
                self.fields['lote'].queryset = DetalhesMedicamento.objects.none()
        else:
            self.fields['lote'].queryset = DetalhesMedicamento.objects.none()


from django import forms
from .models import Distribuicao, DistribuicaoMedicamento

class DistribuicaoForm(forms.ModelForm):
    class Meta:
        model = Distribuicao
        fields = ['estabelecimento_destino']

    def __init__(self, *args, **kwargs):
        user_estabelecimento = kwargs.pop('user_estabelecimento', None)
        super().__init__(*args, **kwargs)
        if user_estabelecimento:
            # Exclui o próprio estabelecimento do campo 'estabelecimento_destino'
            self.fields['estabelecimento_destino'].queryset = Estabelecimento.objects.exclude(
                id=user_estabelecimento.id
            )

from django import forms
from .models import DistribuicaoMedicamento, Medicamento, Estoque

class DistribuicaoMedicamentoForm(forms.ModelForm):
    class Meta:
        model = DistribuicaoMedicamento
        fields = ['medicamento', 'lote', 'quantidade']

    def __init__(self, *args, **kwargs):
        distrib = kwargs.pop('distrib', None)  # Obtem a instância de Distribuicao
        super().__init__(*args, **kwargs)

        # Filtrar medicamentos com estoque maior que zero no estabelecimento de origem
        if distrib and distrib.estabelecimento_origem:
            self.fields['medicamento'].queryset = Medicamento.objects.filter(
                estoques_medicamento__estabelecimento=distrib.estabelecimento_origem,
                estoques_medicamento__quantidade__gt=0
            ).distinct()

        # Filtrar lotes somente se um medicamento for selecionado
        if 'medicamento' in self.data:
            try:
                medicamento_id = int(self.data.get('medicamento'))
                self.fields['lote'].queryset = Estoque.objects.filter(
                    medicamento_id=medicamento_id,
                    estabelecimento=distrib.estabelecimento_origem,
                    quantidade__gt=0
                )
            except (ValueError, TypeError):
                self.fields['lote'].queryset = Estoque.objects.none()
        elif self.instance.pk and self.instance.medicamento:
            # Caso esteja editando, exibir os lotes correspondentes ao medicamento
            self.fields['lote'].queryset = Estoque.objects.filter(
                medicamento=self.instance.medicamento,
                estabelecimento=distrib.estabelecimento_origem,
                quantidade__gt=0
            )
        else:
            self.fields['lote'].queryset = Estoque.objects.none()



