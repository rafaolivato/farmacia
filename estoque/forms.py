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
from datetime import date
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


from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ["nome", "nome_mae", "cns", "cpf", "data_nascimento"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "nome_mae": forms.TextInput(attrs={"class": "form-control"}),
            "cns": forms.TextInput(attrs={"class": "form-control"}),
            "cpf": forms.TextInput(attrs={"class": "form-control"}),
            "data_nascimento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


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
from django.forms import inlineformset_factory
from .models import EntradaEstoque, DetalhesMedicamento

class EntradaEstoqueForm(forms.ModelForm):
    class Meta:
        model = EntradaEstoque
        fields = ['tipo', 'data', 'data_recebimento', 'fonte_financiamento', 'fornecedor_tipo', 'fornecedor', 'tipo_documento', 'numero_documento', 'valor_total', 'observacao'] #removido o campo user
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_recebimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fonte_financiamento': forms.Select(attrs={'class': 'form-control'}),
            'fornecedor_tipo': forms.Select(attrs={'class': 'form-control'}),
            'fornecedor': forms.Select(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        

DetalhesMedicamentoFormSet = inlineformset_factory(
    EntradaEstoque,
    DetalhesMedicamento,
    fields=('medicamento', 'quantidade', 'validade', 'lote', 'valor', 'localizacao', 'fabricante'),
    extra=1,
    
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
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-control w-100'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control w-100'}),
        }


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
from django.forms import inlineformset_factory
from .models import Distribuicao, DistribuicaoMedicamento, DetalhesMedicamento, Medicamento, Estabelecimento, Estoque
from django.db.models import Sum

class DistribuicaoForm(forms.ModelForm):
    class Meta:
        model = Distribuicao
        fields = ['estabelecimento_destino']
        widgets = {
            'estabelecimento_destino': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtém o usuário passado pela view
        super().__init__(*args, **kwargs)


        if user and hasattr(user, 'profile') and user.profile.estabelecimento:
            self.fields['estabelecimento_destino'].queryset = Estabelecimento.objects.exclude(
                id=user.profile.estabelecimento.id
            )

class DistribuicaoMedicamentoForm(forms.ModelForm):
    # Estabelecimento de origem: deve ser fixo e não editável
    estabelecimento_origem = forms.ModelChoiceField(queryset=Estabelecimento.objects.all(), required=False, widget=forms.HiddenInput())

    class Meta:
        model = DistribuicaoMedicamento
        fields = ['medicamento', 'lote', 'quantidade']
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-select', 'onchange': 'atualizarLotes(this)'}),
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, estabelecimento_origem=None, **kwargs):
        super().__init__(*args, **kwargs)
       

        self.fields['medicamento'].queryset = Medicamento.objects.none() 
       

        # Atribui o estabelecimento_origem se passado como argumento
        if estabelecimento_origem:
            self.fields['estabelecimento_origem'].initial = estabelecimento_origem
            self.fields['estabelecimento_origem'].widget = forms.HiddenInput()  # Deixa o campo oculto no formulário
            
               
        if estabelecimento_origem:
            # Filtra os medicamentos disponíveis no estoque do estabelecimento
            medicamentos_disponiveis = Medicamento.objects.filter(
                estoques_medicamento__estabelecimento=estabelecimento_origem
            ).annotate(
                total_estoque=Sum('estoques_medicamento__quantidade')
            ).filter(total_estoque__gt=0).distinct()

            self.fields['medicamento'].queryset = medicamentos_disponiveis

    def clean(self):
        cleaned_data = super().clean()
        lote = cleaned_data.get('lote')
        
        if lote:
            cleaned_data['validade'] = lote.validade  # Associa a validade do lote automaticamente
        
        return cleaned_data



DistribuicaoMedicamentoFormSet = modelformset_factory(
    DistribuicaoMedicamento, form=DistribuicaoMedicamentoForm, extra=1
)

class SaidaEstoqueForm(forms.ModelForm):
    class Meta:
        model = SaidaEstoque
        fields = ['departamento', 'observacao']
        widgets = {
            'departamento': forms.Select(attrs={'class': 'form-control select2'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

       
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
      

from .models import ItemSaida, Medicamento, DetalhesMedicamento, Estoque

class ItemSaidaForm(forms.ModelForm):
    class Meta:
        model = ItemSaida
        fields = ['medicamento', 'lote', 'quantidade']

    def __init__(self, *args, **kwargs):
        estabelecimento = kwargs.pop('estabelecimento', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if estabelecimento:
            # Filtra os medicamentos com estoque > 0 para esse estabelecimento
            medicamentos_com_estoque = Medicamento.objects.filter(
                detalhesmedicamento__quantidade__gt=0,
                detalhesmedicamento__estoque__estabelecimento=estabelecimento
            ).distinct()
            self.fields['medicamento'].queryset = medicamentos_com_estoque
        else:
            # Se não tiver estabelecimento, mostra todos mesmo
            self.fields['medicamento'].queryset = Medicamento.objects.none()

            estabelecimento = None
        if self.user:
            estabelecimento = self.user.profile.estabelecimento
            self.fields['medicamento'].queryset = Medicamento.objects.filter(
                estoque__estabelecimento=estabelecimento
            ).distinct()

            self.fields['lote'].queryset = DetalhesMedicamento.objects.filter(
                estabelecimento=estabelecimento
            )

        # NÃO sobrescreva os querysets filtrados aqui:
        # self.fields['medicamento'].queryset = Medicamento.objects.all()
        # self.fields['lote'].queryset = DetalhesMedicamento.objects.none()

        if 'medicamento' in self.data and estabelecimento:
            try:
                medicamento_id = int(self.data.get('medicamento'))
                self.fields['lote'].queryset = DetalhesMedicamento.objects.filter(
                    medicamento_id=medicamento_id,
                    estabelecimento=estabelecimento
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and estabelecimento:
            self.fields['lote'].queryset = DetalhesMedicamento.objects.filter(
                medicamento=self.instance.medicamento,
                estabelecimento=estabelecimento
            )

    def clean(self):
        cleaned_data = super().clean()
        medicamento = cleaned_data.get('medicamento')
        lote = cleaned_data.get('lote')

        if medicamento and lote and lote.medicamento != medicamento:
            raise forms.ValidationError("O lote selecionado não pertence ao medicamento escolhido.")

 

from django.forms import BaseModelFormSet

class BaseItemSaidaFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['user'] = self.user
        return super()._construct_form(i, **kwargs)


from django import forms
from django.forms import inlineformset_factory
from .models import Requisicao, ItemRequisicao


class RequisicaoForm(forms.ModelForm):
    class Meta:
        model = Requisicao
        fields = ['estabelecimento_destino', 'observacoes']
        widgets = {
            'estabelecimento_destino': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas estabelecimentos do tipo "Almoxarifado Central"
        self.fields['estabelecimento_destino'].queryset = Estabelecimento.objects.filter(tipo_estabelecimento="Almoxarifado Central")

       

      
class ItemRequisicaoForm(forms.ModelForm):
    class Meta:
        model = ItemRequisicao
        fields = ["medicamento", "quantidade"]
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        estabelecimento_destino = kwargs.pop("estabelecimento_destino", None)
        super().__init__(*args, **kwargs)

        if estabelecimento_destino:
            self.fields["medicamento"].queryset = Medicamento.objects.filter(
                estoque__estabelecimento=estabelecimento_destino
            ).distinct()

# Criando um FormSet para adicionar vários medicamentos à requisição
ItemRequisicaoFormSet = inlineformset_factory(
    Requisicao, ItemRequisicao, form=ItemRequisicaoForm,
    extra=1, can_delete=True
)


from django import forms
from django.forms import formset_factory
from .models import DetalhesMedicamento

class LoteSelecionadoForm(forms.Form):
    lote = forms.ModelChoiceField(
        queryset=DetalhesMedicamento.objects.none(), 
        empty_label="Selecione um lote", 
        label="Lote"
    )
    quantidade_selecionada = forms.IntegerField(min_value=1, label="Quantidade")

LoteSelecionadoFormSet = formset_factory(LoteSelecionadoForm, extra=0)


from django import forms
from .models import DetalhesMedicamento

class DetalhesMedicamentoForm(forms.ModelForm):
    class Meta:
        model = DetalhesMedicamento
        fields = ['medicamento', 'lote', 'quantidade', 'validade', 'valor', 'localizacao', 'fabricante']
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-control'}),
            'lote': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'validade': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'localizacao': forms.Select(attrs={'class': 'form-control'}),
            'fabricante': forms.Select(attrs={'class': 'form-control'}),
        }

