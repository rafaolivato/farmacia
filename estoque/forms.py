from django.forms import inlineformset_factory
from datetime import date
from django import forms
from .models import (
    Medicamento,
    Estoque,
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
    PerfilOperador,
    Funcionalidade
    
   
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
    
class EstoqueForm(forms.ModelForm):
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
        model = Estoque
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
            "valor": forms.TextInput(
                attrs={
                    "placeholder": "0,00",
                    "class": "form-control form-control-sm currency-input",
                }
            ),
        }

DetalhesMedicamentoFormSet = inlineformset_factory(
    Estoque,
    DetalhesMedicamento,
    form=DetalhesMedicamentoForm,
    extra=1,
    can_delete=False,
)

class EstabelecimentoForm(forms.ModelForm):
    class Meta:
        model = Estabelecimento
        fields = ['nome', 'codigo_cnes', 'farmaceutico_responsavel', 'imagem_logotipo', 'tipo_estabelecimento']


from django import forms
from .models import Operador, Estabelecimento

class OperadorForm(forms.ModelForm):
    funcionalidades = forms.ModelMultipleChoiceField(
        queryset=Funcionalidade.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Operador
        fields = ['nome_completo', 'email', 'cpf', 'perfil', 'estabelecimentos', 'funcionalidades']

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
from .models import DetalhesMedicamento


class SaidaEstoqueForm(forms.Form):
    # Retorna todos os medicamentos com quantidade > 0, e os medicamentos duplicados são filtrados manualmente no Python
    medicamento = forms.ModelChoiceField(
        queryset=DetalhesMedicamento.objects.filter(quantidade__gt=0).order_by('medicamento'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantidade = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    lote = forms.ModelChoiceField(
        queryset=DetalhesMedicamento.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(SaidaEstoqueForm, self).__init__(*args, **kwargs)
        
        # Pegamos os medicamentos disponíveis em estoque
        medicamentos_com_estoque = DetalhesMedicamento.objects.filter(quantidade__gt=0).order_by('medicamento')
        
        # Eliminamos os duplicados
        medicamentos_distintos = {medicamento.medicamento for medicamento in medicamentos_com_estoque}
        
        # Atualizamos o queryset do campo medicamento
        self.fields['medicamento'].queryset = DetalhesMedicamento.objects.filter(medicamento__in=medicamentos_distintos)

        if 'medicamento' in self.data:
            try:
                medicamento_id = int(self.data.get('medicamento'))
                self.fields['lote'].queryset = DetalhesMedicamento.objects.filter(medicamento=medicamento_id)
            except (ValueError, TypeError):
                self.fields['lote'].queryset = DetalhesMedicamento.objects.none()
        else:
            self.fields['lote'].queryset = DetalhesMedicamento.objects.none()



    

    






