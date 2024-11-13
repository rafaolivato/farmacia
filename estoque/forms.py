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

# FormSet para DetalhesMedicamento
DetalhesMedicamentoFormSet = modelformset_factory(
    DetalhesMedicamento,
    form=DetalhesMedicamentoForm,
    extra=1
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


# forms.py

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
from .models import SaidaEstoque, DetalhesMedicamento, Medicamento, Departamento

class SaidaEstoqueForm(forms.ModelForm):
    class Meta:
        model = SaidaEstoque
        fields = ['departamento', 'medicamento', 'quantidade', 'lote']
        widgets = {
            'departamento': forms.Select(attrs={'id': 'id_departamento', 'name': 'departamento', 'class': 'form-control select2'}),
            'medicamento': forms.Select(attrs={'id': 'id_medicamento', 'name': 'medicamento', 'class': 'form-control select2'}),
            'quantidade': forms.NumberInput(attrs={'id': 'id_quantidade', 'name': 'quantidade', 'class': 'form-control'}),
            'lote': forms.Select(attrs={'id': 'id_lote', 'name': 'lote', 'class': 'form-control select2'}),
        }
    
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
