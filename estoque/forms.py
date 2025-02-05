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
from .models import EntradaEstoque, DetalhesMedicamento, Medicamento, Fabricante, Localizacao

class EntradaEstoqueForm(forms.ModelForm):
    valor_total = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'form-control valor-total', 'placeholder': 'R$ 0,00'}),
        initial=0.00
    )

    class Meta:
        model = EntradaEstoque
        fields = ['tipo', 'data', 'data_recebimento', 'fornecedor', 'tipo_documento', 'numero_documento', 'valor_total', 'observacao']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_recebimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fornecedor': forms.Select(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_total': forms.TextInput(attrs={'class': 'form-control valor-total'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_valor_total(self):
        valor = self.cleaned_data.get('valor_total')
        if isinstance(valor, str):
            valor = valor.replace(".", "").replace(",", ".").replace("R$", "").strip()  # Converte 1.000,50 para 1000.50
        try:
            return float(valor)
        except ValueError:
            raise forms.ValidationError("Digite um número válido.")

    

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retira 'user' de kwargs
        super().__init__(*args, **kwargs)
        
        if user and user.profile.estabelecimento:
            self.instance.estabelecimento = user.profile.estabelecimento


from django import forms
from .models import DetalhesMedicamento, Estoque, Medicamento, Fabricante, Localizacao
from django.forms import modelformset_factory

class DetalhesMedicamentoForm(forms.ModelForm):
    valor = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'form-control valor-campo', 'placeholder': 'R$ 0,00'}),
        initial=0.00
    )

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if isinstance(valor, str):
            valor = valor.replace(".", "").replace(",", ".")  # Converte 1.000,50 para 1000.50
        try:
            return float(valor)
        except ValueError:
            raise forms.ValidationError("Digite um número válido.")

    class Meta:
        model = DetalhesMedicamento
        fields = ['medicamento', 'quantidade', 'localizacao', 'validade', 'lote', 'valor', 'fabricante']

 

# FormSet para DetalhesMedicamento
DetalhesMedicamentoFormSet = modelformset_factory(
    DetalhesMedicamento,
    fields=('medicamento', 'quantidade', 'localizacao', 'validade', 'lote', 'valor', 'fabricante'),
   widgets={
    'medicamento': forms.Select(attrs={'class': 'form-control select2', 'style': 'max-width: 300px;'}),
    'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'style': 'max-width: 120px;'}),
    'lote': forms.TextInput(attrs={'class': 'form-control', 'style': 'max-width: 200px;'}),
    'valor': forms.TextInput(attrs={'class': 'form-control valor-campo', 'style': 'max-width: 150px;'}),
    'localizacao': forms.Select(attrs={'class': 'form-control select2', 'style': 'max-width: 250px;'}),
    'validade': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'max-width: 200px;'}),
    'fabricante': forms.Select(attrs={'class': 'form-control select2', 'style': 'max-width: 250px;'})
},
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
from .models import Distribuicao, Estabelecimento

class DistribuicaoForm(forms.ModelForm):
   
    class Meta:
        model = Distribuicao
        fields = ['estabelecimento_destino']
        widgets = {
            'estabelecimento_destino': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, estabelecimento_origem=None, **kwargs):
        super().__init__(*args, **kwargs)
        if estabelecimento_origem:
            # Excluir o estabelecimento de origem da queryset
            self.fields['estabelecimento_destino'].queryset = Estabelecimento.objects.exclude(id=estabelecimento_origem.id)
        else:
            # Se não houver estabelecimento de origem, mantém a queryset vazia
            self.fields['estabelecimento_destino'].queryset = Estabelecimento.objects.none()


from django import forms
from .models import Medicamento, DetalhesMedicamento, Estabelecimento

class DistribuicaoMedicamentoForm(forms.Form):
    medicamento = forms.ModelChoiceField(
        queryset=Medicamento.objects.none(),
        label="Medicamento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    lote = forms.ModelChoiceField(
        queryset=DetalhesMedicamento.objects.none(),
        label="Lote",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantidade = forms.IntegerField(
        label="Quantidade",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    estabelecimento_destino = forms.ModelChoiceField(
        queryset=Estabelecimento.objects.none(),
        label="Estabelecimento Destino",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        estabelecimento_origem = kwargs.pop('estabelecimento_origem', None)
        super().__init__(*args, **kwargs)

        if estabelecimento_origem:
            # Filtrar medicamentos disponíveis no estoque do estabelecimento logado
            medicamentos_disponiveis = Medicamento.objects.filter(
                detalhesmedicamento__estabelecimento=estabelecimento_origem,
                detalhesmedicamento__quantidade__gt=0
            ).distinct()

            self.fields['medicamento'].queryset = medicamentos_disponiveis

            # Filtrar lotes do estabelecimento logado
            self.fields['lote'].queryset = DetalhesMedicamento.objects.filter(
                estabelecimento=estabelecimento_origem,
                quantidade__gt=0
            )

            # Excluir o estabelecimento logado da lista de destinos
            self.fields['estabelecimento_destino'].queryset = Estabelecimento.objects.exclude(
                id=estabelecimento_origem.id
            )


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
                estoques_medicamento__estabelecimento=estabelecimento,
                estoques_medicamento__quantidade__gt=0  # Filtra apenas os medicamentos com estoque > 0
            ).distinct()

    # Se o medicamento já está selecionado, carregue os lotes correspondentes
        if 'medicamento' in self.data:
            try:
                medicamento_id = int(self.data.get('medicamento'))
                self.fields['lote'].queryset = DetalhesMedicamento.objects.filter(
                    medicamento_id=medicamento_id,
                    estabelecimento=estabelecimento,
                    quantidade__gt=0  # Filtra apenas os lotes com estoque > 0
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
        widgets = {
            'estabelecimento_destino': forms.Select(attrs={'class': 'form-control'}),
        }
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
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-control', 'id': 'id_medicamento'}),
            'lote': forms.Select(attrs={'class': 'form-control', 'id': 'id_lote'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            
        }
    def __init__(self, *args, **kwargs):
        distrib = kwargs.pop('distrib', None)
        super().__init__(*args, **kwargs)

        self.fields['lote'].queryset = Estoque.objects.none()  # Inicialmente vazio

        if distrib and distrib.estabelecimento_origem:
            self.fields['medicamento'].queryset = Medicamento.objects.filter(
                estoques_medicamento__estabelecimento=distrib.estabelecimento_origem,
                estoques_medicamento__quantidade__gt=0
            ).distinct()

        if self.instance.pk and self.instance.medicamento:
            self.fields['lote'].queryset = Estoque.objects.filter(
                medicamento=self.instance.medicamento,
                estabelecimento=distrib.estabelecimento_origem,
                quantidade__gt=0
            )




