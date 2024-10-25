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
    Operador,
    Medico,
    Dispensacao,
    DispensacaoMedicamento,
   
)


from django.forms import modelformset_factory
from django.db.models import signals
from django import forms
from django.forms import formset_factory

class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['codigo_identificacao', 'nome', 'psicotropico']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['psicotropico'].widget = forms.Select(choices=self.Meta.model.LISTA_CHOICES)

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
    
class EntradaEstoqueForm(forms.ModelForm):
    valor_total = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "type": "number",
                "step": "0.01",
                "placeholder": "0.00",
                "class": "form-control form-control-sm",
            }
        ),
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        model = EntradaEstoque
        fields = "__all__"
        widgets = {
            "data": forms.DateInput(
                format="%d/%m/%Y",
                attrs={
                    "placeholder": "DD/MM/AAAA",
                    "class": "form-control form-control-sm",
                },
            ),
            "data_recebimento": forms.DateInput(
                format="%d/%m/%Y",
                attrs={
                    "placeholder": "DD/MM/AAAA",
                    "class": "form-control form-control-sm",
                },
            ),
            "numero_documento": forms.TextInput(
                attrs={
                    "placeholder": "Número do Documento",
                    "class": "form-control form-control-sm",
                }
            ),
            "observacao": forms.TextInput(
                attrs={
                    "placeholder": "Observação",
                    "class": "form-control form-control-sm",
                }
            ),
        }

    # Método init para depurar e verificar dados iniciais
    def __init__(self, *args, **kwargs):
        super(EntradaEstoqueForm, self).__init__(*args, **kwargs)
        # Exibir valores iniciais no log para verificação
        print("EntradaEstoqueForm - Valores Iniciais:", self.initial)


from django import forms
from .models import DetalhesMedicamento, Localizacao, Fabricante

class DetalhesMedicamentoForm(forms.ModelForm):
    localizacao = forms.ModelChoiceField(
        queryset=Localizacao.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control form-control-sm wider-placeholder",
                "placeholder": "Selecione a localização",
                "style": "width: 50%;",  # Ajusta a largura do campo
            }
        ),
        required=False,
        label="Localização"
    )
    fabricante = forms.ModelChoiceField(
        queryset=Fabricante.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control form-control-sm",
                "placeholder": "Selecione um fabricante",
            }
        ),
        required=False,
        label="Fabricante"
    )

    class Meta:
        model = DetalhesMedicamento
        fields = "__all__"
        widgets = {
            "validade": forms.DateInput(
                format="%d/%m/%Y",
                attrs={
                    "placeholder": "DD/MM/AAAA",
                    "class": "form-control form-control-sm",
                },
            ),
            "lote": forms.TextInput(
                attrs={
                    "placeholder": "Lote",
                    "class": "form-control form-control-sm",
                }
            ),
            "valor": forms.NumberInput(
                attrs={
                    "placeholder": "0.00",
                    "class": "form-control form-control-sm",
                    "step": "0.01",
                }
            ),
        }

    # Método init para depurar e verificar dados iniciais
    def __init__(self, *args, **kwargs):
        super(DetalhesMedicamentoForm, self).__init__(*args, **kwargs)
        # Exibir valores iniciais no log para verificação
        print("DetalhesMedicamentoForm - Valores Iniciais:", self.initial)

from django.forms import inlineformset_factory
from .models import EntradaEstoque, DetalhesMedicamento

# Definição do FormSet para DetalhesMedicamento
DetalhesMedicamentoFormSet = inlineformset_factory(
    EntradaEstoque,
    DetalhesMedicamento,
    form=DetalhesMedicamentoForm,  # Certifique-se de que DetalhesMedicamentoForm está definido antes
    extra=1,
    can_delete=True
)


class EstabelecimentoForm(forms.ModelForm):
    class Meta:
        model = Estabelecimento
        fields = ['nome', 'codigo_cnes', 'farmaceutico_responsavel', 'imagem_logotipo', 'tipo_estabelecimento']


from django import forms
from .models import Operador, Estabelecimento
from .estabelecimento import Estabelecimento

class OperadorForm(forms.ModelForm):
    class Meta:
        model = Operador
        fields = ['username', 'nome_completo', 'email', 'cpf', 'estabelecimentos']
        widgets = {
            'estabelecimentos': forms.SelectMultiple(attrs={'class': 'select2'}),
        }
        
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
from .models import SaidaEstoque, DetalhesMedicamento, Departamento, Medicamento

class SaidaEstoqueForm(forms.ModelForm):
    class Meta:
        model = SaidaEstoque
        fields = ['departamento', 'medicamento', 'quantidade', 'lote']
    
    def __init__(self, *args, **kwargs):
        super(SaidaEstoqueForm, self).__init__(*args, **kwargs)
        
        self.fields['departamento'].queryset = Departamento.objects.all()
        
        # Inicialmente, o campo `lote` não terá opções, pois será preenchido dinamicamente
        self.fields['lote'].queryset = DetalhesMedicamento.objects.none()
        
        medicamentos_com_estoque = Medicamento.objects.filter(
            detalhesmedicamento__quantidade__gt=0
        ).distinct()
        self.fields['medicamento'].queryset = medicamentos_com_estoque

        # Verifica se já existe um medicamento selecionado para carregar os lotes correspondentes
        if 'medicamento' in self.data:
            try:
                medicamento_id = int(self.data.get('medicamento'))
                self.fields['lote'].queryset = DetalhesMedicamento.objects.filter(medicamento_id=medicamento_id, quantidade__gt=0).order_by('lote')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # Se o objeto já existir, filtra o lote com base no medicamento do objeto
            self.fields['lote'].queryset = self.instance.medicamento.detalhesmedicamento_set.filter(quantidade__gt=0).order_by('lote')


from django import forms
from .models import Distribuicao, DistribuicaoMedicamento, DetalhesMedicamento, Estabelecimento

class DistribuicaoForm(forms.ModelForm):
    class Meta:
        model = Distribuicao
        fields = ['estabelecimento_destino']
        widgets = {
            'estabelecimento_destino': forms.Select(attrs={'class': 'form-select'}),
        }

from django import forms
from .models import DistribuicaoMedicamento, Medicamento

class DistribuicaoMedicamentoForm(forms.ModelForm):
    class Meta:
        model = DistribuicaoMedicamento
        fields = ['medicamento', 'quantidade']
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar medicamentos em ordem alfabética
        self.fields['medicamento'].queryset = Medicamento.objects.all().order_by('nome')


from django import forms
from .models import Requisicao, ItemRequisicao, Estabelecimento, Medicamento

class RequisicaoForm(forms.ModelForm):
    class Meta:
        model = Requisicao
        fields = ['estabelecimento_destino']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estabelecimento_destino'].queryset = Estabelecimento.objects.filter(tipo_estabelecimento='Almoxarifado Central')

class ItemRequisicaoForm(forms.ModelForm):
    class Meta:
        model = ItemRequisicao
        fields = ['medicamento', 'quantidade']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medicamento'].queryset = Medicamento.objects.all()