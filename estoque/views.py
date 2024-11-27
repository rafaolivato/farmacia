from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
    Medicamento,
    DispensacaoMedicamento,
    EntradaEstoque,
    Paciente,
    Fornecedor,
    DetalhesMedicamento,
    Localizacao,
    Fabricante,
    Estabelecimento,
    Departamento,
    SaidaEstoque,
    Dispensacao,
    DistribuicaoMedicamento,
    Requisicao,
    Estoque
)


from .forms import (
    MedicamentoForm,
    PacienteForm,
    FornecedorForm,
    EntradaEstoqueForm,
    DetalhesMedicamentoFormSet,
    DetalhesMedicamentoForm,
    LocalizacaoForm,
    FabricanteForm,
    EstabelecimentoForm,
    DepartamentoForm,
    SaidaEstoqueForm,
    MedicoForm,
    DispensacaoForm,
    DispensacaoMedicamentoFormSet,
    LoginForm,
    
)
from django.db.models import Sum
from django.utils import timezone
from django.db import connection
from datetime import timedelta, date
from django.http import JsonResponse
from django.db import transaction
import os
import pandas as pd
from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.forms import formset_factory


from django.db.models import F, Sum
from django.utils import timezone
from datetime import timedelta
from .models import DetalhesMedicamento

# autenticacao/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

def base(request):
    return render(request, "estoque/base.html")  
    
   
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required

@login_required
def lista_medicamentos(request):
    # Data atual
    now = timezone.now()
    # Data 3 meses à frente
    now_plus_3_months = (now + timedelta(days=90)).date()

    # Obter o estabelecimento do usuário logado
    estabelecimento = request.user.profile.estabelecimento

    # Filtrar os medicamentos do estabelecimento
    detalhes_medicamentos = (
        DetalhesMedicamento.objects.filter(estoque__estabelecimento=estabelecimento)
        .values("medicamento__id", "medicamento__nome", "localizacao", "validade", "lote")
        .annotate(
            total_quantidade=Sum("quantidade"),
            total_valor=Sum(F("quantidade") * F("valor"))
        )
        .order_by("medicamento__nome", "lote")
    )

    return render(
        request,
        "estoque/lista_medicamentos.html",
        {
            "detalhes_medicamentos": detalhes_medicamentos,
            "now_plus_3_months": now_plus_3_months,
        },
    )


def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    query = request.GET.get("q")
    if query:
        pacientes = pacientes.filter(nome__icontains=query)
    return render(request, "estoque/lista_pacientes.html", {"pacientes": pacientes})


@login_required
def novo_paciente(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_pacientes")
    else:
        form = PacienteForm()
    return render(request, "estoque/novo_paciente.html", {"form": form})


@login_required
def cadastro_fornecedor(request):
    if request.method == "POST":
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fornecedor cadastrado com sucesso.")
            return redirect("entrada_estoque")
        else:
            messages.error(request, "Erro ao cadastrar fornecedor.")
    else:
        form = FornecedorForm()
    return render(request, "estoque/cadastro_fornecedor.html", {"form": form})


@login_required
def cadastro_fabricante(request):
    if request.method == "POST":
        form = FabricanteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fabricante cadastrado com sucesso.")
            return redirect("entrada_estoque")
        else:
            messages.error(request, "Erro ao cadastrar fabricante.")
    else:
        form = FabricanteForm()
    return render(request, "estoque/cadastro_fabricante.html", {"form": form})


from estoque.models import Estabelecimento

def carregar_medicamentos_excel(request):
    # Diretório onde os arquivos Excel estão localizados
    excel_dir = os.path.join(settings.MEDIA_ROOT, "excel")
    excel_files = [
        "codigos_corretos.xlsx",
    ]

    # Obter o estabelecimento padrão para os medicamentos importados
    estabelecimento_padrao = Estabelecimento.objects.get(nome="Almoxarifado Central")

    for file_name in excel_files:
        file_path = os.path.join(excel_dir, file_name)
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            for index, row in df.iterrows():
                Medicamento.objects.update_or_create(
                    codigo_identificacao=row["Código"],
                    defaults={
                        "nome": row["Nome"],
                        "estabelecimento": estabelecimento_padrao,  # Define o estabelecimento padrão
                    }
                )

    return redirect("lista_medicamentos")




@login_required
def cadastrar_medicamento(request):
    medicamentos = Medicamento.objects.all()
    if request.method == "POST":
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sucesso")
    else:
        form = MedicamentoForm()
    return render(
        request,
        "estoque/cadastrar_medicamento.html",
        {"form": form, "medicamentos": medicamentos},
    )


def sucesso(request):
    return render(request, "estoque/sucesso.html")


@login_required
def cadastrar_localizacao(request):
    if request.method == "POST":
        form = LocalizacaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Localização cadastrada com sucesso.")
            return redirect("lista_localizacoes")
        else:
            messages.error(request, "Erro ao cadastrar localização.")
    else:
        form = LocalizacaoForm()
    return render(request, "estoque/cadastrar_localizacao.html", {"form": form})


def lista_localizacoes(request):
    localizacoes = Localizacao.objects.all()
    return render(
        request, "estoque/lista_localizacoes.html", {"localizacoes": localizacoes}
    )

from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import EntradaEstoqueForm, DetalhesMedicamentoFormSet
from .models import Estoque, EntradaEstoque, DetalhesMedicamento

@login_required
def entrada_estoque_view(request):
    if request.method == 'POST':
        entrada_form = EntradaEstoqueForm(request.POST, user=request.user)
        detalhes_formset = DetalhesMedicamentoFormSet(request.POST)

        if entrada_form.is_valid() and detalhes_formset.is_valid():
            with transaction.atomic():
                # Salva a entrada
                entrada = entrada_form.save(commit=False)
                entrada.user = request.user
                entrada.save()

                # Salva os detalhes dos medicamentos
                for form in detalhes_formset:
                    detalhe = form.save(commit=False)
                    detalhe.entrada = entrada
                    detalhe.estabelecimento = entrada.estabelecimento  # Associa o estabelecimento à entrada

                    # Verifica ou cria o estoque associado
                    estoque, created = Estoque.objects.get_or_create(
                        medicamento=detalhe.medicamento,
                        estabelecimento=entrada.estabelecimento,
                        defaults={'quantidade': detalhe.quantidade}
                    )

                    # Atualiza a quantidade no estoque
                    if not created:
                        estoque.quantidade += detalhe.quantidade
                        estoque.save()

                    # Associa o estoque ao detalhe e salva
                    detalhe.estoque = estoque
                    detalhe.save()

                messages.success(request, 'Entrada de medicamentos concluída com sucesso.')
                return redirect('sucesso')

    else:
        entrada_form = EntradaEstoqueForm(user=request.user)
        detalhes_formset = DetalhesMedicamentoFormSet(queryset=DetalhesMedicamento.objects.none())

    return render(request, 'estoque/entrada_estoque.html', {
        'entrada_form': entrada_form,
        'detalhes_formset': detalhes_formset,
    })





@login_required
def cadastrar_estabelecimento(request):
    if request.method == "POST":
        form = EstabelecimentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Estabelecimento cadastrado com sucesso.")
            return redirect("lista_estabelecimentos")
        else:
            messages.error(request, "Erro ao cadastrar estabelecimento.")
    else:
        form = EstabelecimentoForm()
    return render(request, "estoque/cadastrar_estabelecimento.html", {"form": form})


def lista_estabelecimentos(request):
    estabelecimentos = Estabelecimento.objects.all()
    return render(
        request,
        "estoque/lista_estabelecimentos.html",
        {"estabelecimentos": estabelecimentos},
    )


@login_required
def cadastrar_departamento(request):
    if request.method == "POST":
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Departamento cadastrado com sucesso.")
            return redirect("lista_departamento")
        else:
            messages.error(request, "Erro ao cadastrar departamento.")
    else:
        form = DepartamentoForm()
    return render(request, "estoque/cadastrar_departamento.html", {"form": form})


def lista_departamento(request):
    departamentos = Departamento.objects.all()
    return render(
        request, "estoque/lista_departamento.html", {"departamentos": departamentos}
    )

def is_admin(user):
    return user.is_staff


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["operador"],
                password=form.cleaned_data["senha"],
            )
            if user is not None:
                login(request, user)
                return redirect("estoque/base")
            else:
                messages.error(request, "Operador inválido")
    else:
        form = LoginForm()
    return render(request, "estoque/login.html", {"form": form})


from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect

class CustomLogoutView(LogoutView):
    def get_next_page(self):
        return '/'  # Redirecione para a página desejada



@login_required
def cadastrar_medico(request):
    if request.method == "POST":
        form = MedicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Médico cadastrado com sucesso!")
            return redirect("cadastrar_medico")  # Redirect to avoid form resubmission
    else:
        form = MedicoForm()

    return render(request, "estoque/cadastrar_medico.html", {"form": form})


def listar_dispensacoes(request):
    dispensacoes = Dispensacao.objects.all()
    return render(
        request, "estoque/listar_dispensacoes.html", {"dispensacoes": dispensacoes}
    )

@login_required
def nova_dispensacao(request):
    if request.method == "POST":
        form = DispensacaoForm(request.POST)
        formset = DispensacaoMedicamentoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            dispensacao = form.save()
            medicamentos = formset.save(commit=False)
            for medicamento in medicamentos:
                medicamento.dispensacao = dispensacao
                medicamento.save()
            messages.success(request, "Dispensação registrada com sucesso!")
            return redirect("listar_dispensacoes")
    else:
        medicamentos_com_estoque = Medicamento.objects.filter(
            detalhesmedicamento__quantidade__gt=0
        ).distinct()

    form = DispensacaoForm()
    formset = DispensacaoMedicamentoFormSet(
        queryset=DispensacaoMedicamento.objects.none()
    )

    # Obter dispensações recentes
    dispensacoes_recentes = Dispensacao.objects.all().order_by("-data_dispensacao")[:3]

    return render(
        request,
        "estoque/nova_dispensacao.html",
        {
            "form": form,
            "formset": formset,
            "medicamentos_disponiveis": medicamentos_com_estoque,
            "dispensacoes_recentes": dispensacoes_recentes,
        },
    )


def detalhes_dispensacao(request, id):
    dispensacao = Dispensacao.objects.get(id=id)
    dispensacoes_recentes = Dispensacao.objects.order_by("-data_dispensacao")[:5]
    context = {
        "dispensacao": dispensacao,
        "dispensacoes_recentes": dispensacoes_recentes,
    }
    return render(request, "estoque/detalhes_dispensacao.html", context)

from django.http import JsonResponse
from .models import DetalhesMedicamento


def lotes_por_medicamento(request, medicamento_id):
    if request.method == 'GET':
        estabelecimento_id = request.GET.get('estabelecimento_id')
        try:
            lotes = DetalhesMedicamento.objects.filter(
                medicamento_id=medicamento_id,
                estoque__estabelecimento_id=estabelecimento_id,
                quantidade__gt=0
            ).values('id', 'lote', 'quantidade')
            
            if lotes:
                return JsonResponse({'lotes': list(lotes)})
            else:
                return JsonResponse({'error': 'Nenhum lote encontrado para o medicamento informado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método de requisição inválido'}, status=400)



from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import SaidaEstoqueForm
from .models import SaidaEstoque, DetalhesMedicamento

def saida_estoque(request):
    estabelecimento = request.user.profile.estabelecimento 
    

    if request.method == 'POST':
        form = SaidaEstoqueForm(request.POST, estabelecimento=estabelecimento)
        if form.is_valid():
            # Preencher a data de atendimento
            saida = form.save(commit=False)
            saida.data_atendimento = timezone.now()  # Data de atendimento
            saida.save()

            # Atualizar a quantidade do lote no estoque
            medicamento = form.cleaned_data['medicamento']
            lote = form.cleaned_data['lote']
            quantidade = form.cleaned_data['quantidade']

            # Encontrar o lote correspondente
            detalhes_medicamento = DetalhesMedicamento.objects.get(id=lote.id)

            # Verificar se há quantidade suficiente
            if detalhes_medicamento.quantidade >= quantidade:
                # Atualizar a quantidade do lote
                detalhes_medicamento.quantidade -= quantidade
                detalhes_medicamento.save()
            else:
                # Caso a quantidade seja insuficiente
                form.add_error('quantidade', 'Estoque insuficiente para esse medicamento.')

            return redirect('sucesso')  # Redireciona para a página de sucesso após salvar
    else:
        form = SaidaEstoqueForm()

    return render(request, 'estoque/saida_estoque.html', {'form': form})









from django.http import JsonResponse
from .models import DetalhesMedicamento

def get_lotes(request, medicamento_id):
    lotes = DetalhesMedicamento.objects.filter(
        medicamento_id=medicamento_id, quantidade__gt=0
    ).values("id", "lote")
    return JsonResponse({"lotes": list(lotes)})


from django.shortcuts import render, redirect
from .forms import DistribuicaoForm, DistribuicaoMedicamentoForm
from django.forms import modelformset_factory
from .models import DistribuicaoMedicamento, DetalhesMedicamento, Estabelecimento, Medicamento
from django.db import transaction
from django.contrib import messages

@transaction.atomic
def distribuicao_sem_requisicao(request):
    DistribuicaoMedicamentoFormSet = modelformset_factory(DistribuicaoMedicamento, form=DistribuicaoMedicamentoForm, extra=1)

    if request.method == 'POST':
        distribuicao_form = DistribuicaoForm(request.POST)
        medicamento_formset = DistribuicaoMedicamentoFormSet(request.POST)
        
        if distribuicao_form.is_valid() and medicamento_formset.is_valid():
            distribuicao = distribuicao_form.save(commit=False)
            estabelecimento_origem = Estabelecimento.objects.get(tipo_estabelecimento='Almoxarifado Central')
            estabelecimento_destino = distribuicao.estabelecimento_destino

            # Verificar se o estabelecimento de origem e destino são diferentes
            if estabelecimento_origem == estabelecimento_destino:
                distribuicao_form.add_error('estabelecimento_destino', 'O estabelecimento de origem e destino não podem ser o mesmo.')
            else:
                distribuicao.estabelecimento_origem = estabelecimento_origem
                distribuicao.save()
                
                medicamentos = medicamento_formset.save(commit=False)
                for medicamento in medicamentos:
                    medicamento.distribuicao = distribuicao

                    # Obter a instância do medicamento
                    medicamento_instancia = Medicamento.objects.get(id=medicamento.medicamento.id)
                    medicamento.medicamento = medicamento_instancia

                    # Preenche automaticamente os campos 'lote' e 'validade'
                    detalhes = DetalhesMedicamento.objects.filter(medicamento=medicamento_instancia, quantidade__gt=0).first()
                    if detalhes:
                        medicamento.lote = detalhes.lote
                        medicamento.validade = detalhes.validade

                        # Subtrai a quantidade do estoque
                        if detalhes.quantidade >= medicamento.quantidade:
                            detalhes.quantidade -= medicamento.quantidade
                            detalhes.save()
                        else:
                            messages.error(request, f"Quantidade insuficiente no lote {detalhes.lote} para o medicamento {medicamento_instancia.nome}.")
                            return render(request, 'estoque/distribuicao_sem_requisicao.html', {
                                'distribuicao_form': distribuicao_form,
                                'medicamento_formset': medicamento_formset,
                            })
                    else:
                        messages.error(request, f"Medicamento {medicamento_instancia.nome} não encontrado em estoque.")
                        return render(request, 'estoque/distribuicao_sem_requisicao.html', {
                            'distribuicao_form': distribuicao_form,
                            'medicamento_formset': medicamento_formset,
                        })

                    medicamento.save()
                
                return redirect('consultar_distribuicoes')
    
    else:
        distribuicao_form = DistribuicaoForm()
        medicamento_formset = DistribuicaoMedicamentoFormSet(queryset=DistribuicaoMedicamento.objects.none())
        
        # Filtra os medicamentos disponíveis em estoque com quantidade > 0
        medicamentos_disponiveis = DetalhesMedicamento.objects.filter(quantidade__gt=0).order_by('medicamento__nome')
        
        for form in medicamento_formset:
            form.fields['medicamento'].queryset = Medicamento.objects.filter(id__in=medicamentos_disponiveis.values('medicamento'))

    return render(request, 'estoque/distribuicao_sem_requisicao.html', {
        'distribuicao_form': distribuicao_form,
        'medicamento_formset': medicamento_formset,
    })

from django.shortcuts import render
from .models import Distribuicao

def consultar_distribuicoes(request):
    distribuicoes = Distribuicao.objects.all().order_by('-data_atendimento')
    return render(request, 'estoque/consultar_distribuicoes.html', {'distribuicoes': distribuicoes})

from django.shortcuts import render, redirect
from .forms import RequisicaoForm, ItemRequisicaoForm
from .models import Requisicao, ItemRequisicao, Estabelecimento
from django.forms import modelformset_factory
from django.contrib import messages

def nova_requisicao(request):
    ItemRequisicaoFormSet = modelformset_factory(ItemRequisicao, form=ItemRequisicaoForm, extra=1)

    if request.method == 'POST':
        requisicao_form = RequisicaoForm(request.POST)
        item_formset = ItemRequisicaoFormSet(request.POST, queryset=ItemRequisicao.objects.none())

        if requisicao_form.is_valid() and item_formset.is_valid():
            requisicao = requisicao_form.save(commit=False)
            requisicao.estabelecimento_origem = Estabelecimento.objects.get(nome='UBS Jardim Planalto')  # Ajuste conforme necessário
            requisicao.save()

            for form in item_formset:
                item = form.save(commit=False)
                item.requisicao = requisicao
                item.save()

            messages.success(request, 'Requisição criada com sucesso.')
            return redirect('consultar_requisicoes')
        else:
            messages.error(request, 'Erro ao criar a requisição. Verifique os dados e tente novamente.')
    else:
        requisicao_form = RequisicaoForm()
        item_formset = ItemRequisicaoFormSet(queryset=ItemRequisicao.objects.none())

    return render(request, 'estoque/nova_requisicao.html', {
        'requisicao_form': requisicao_form,
        'item_formset': item_formset,
    })

from django.shortcuts import render
from .models import Requisicao

def consultar_requisicoes(request):
    requisicoes = Requisicao.objects.all()
    return render(request, 'estoque/consultar_requisicoes.html', {'requisicoes': requisicoes})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Requisicao, ItemRequisicao, DetalhesMedicamento
from .forms import ItemRequisicaoForm

def atender_requisicao(request, requisicao_id):
    requisicao = get_object_or_404(Requisicao, id=requisicao_id)
    itens = requisicao.itens.all()

    if request.method == 'POST':
        for item in itens:
            form = ItemRequisicaoForm(request.POST, instance=item)
            if form.is_valid():
                item = form.save(commit=False)
                detalhes = DetalhesMedicamento.objects.filter(medicamento=item.medicamento, quantidade__gt=0).first()
                if detalhes:
                    item.lote = detalhes.lote
                    item.validade = detalhes.validade
                    if detalhes.quantidade >= item.quantidade:
                        detalhes.quantidade -= item.quantidade
                        detalhes.save()
                        item.save()
                    else:
                        messages.error(request, f"Quantidade insuficiente no lote {detalhes.lote} para o medicamento {item.medicamento.nome}.")
                        return render(request, 'estoque/atender_requisicao.html', {'requisicao': requisicao, 'itens': itens})
                else:
                    messages.error(request, f"Medicamento {item.medicamento.nome} não encontrado em estoque.")
                    return render(request, 'estoque/atender_requisicao.html', {'requisicao': requisicao, 'itens': itens})

        requisicao.status = 'Atendida'
        requisicao.save()
        return redirect('consultar_requisicoes')

    return render(request, 'estoque/atender_requisicao.html', {'requisicao': requisicao, 'itens': itens})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Requisicao

@login_required
def aprovar_requisicao(request, requisicao_id):
    requisicao = get_object_or_404(Requisicao, id=requisicao_id)

    if requisicao.status != 'Pendente':
        messages.error(request, "Esta requisição já foi processada.")
        return redirect('detalhe_requisicao', pk=requisicao_id)  # Aqui você deve usar 'pk' se essa é a chave definida na URL

    requisicao.aprovar(usuario=request.user)
    messages.success(request, "Requisição aprovada com sucesso.")
    return redirect('detalhe_requisicao', pk=requisicao_id)  # Mudança aqui também

@login_required
def rejeitar_requisicao(request, requisicao_id):
    requisicao = get_object_or_404(Requisicao, id=requisicao_id)

    if requisicao.status != 'Pendente':
        messages.error(request, "Esta requisição já foi processada.")
        return redirect('detalhe_requisicao', pk=requisicao_id)  # Aqui você deve usar 'pk' se essa é a chave definida na URL

    requisicao.rejeitar(usuario=request.user)
    messages.success(request, "Requisição rejeitada.")
    return redirect('detalhe_requisicao', pk=requisicao_id)  # Mudança aqui também


@login_required
def confirmar_transferencia(request, requisicao_id):
    requisicao = get_object_or_404(Requisicao, id=requisicao_id)

    if requisicao.status != 'Aprovada':
        messages.error(request, "A transferência só pode ser confirmada para requisições aprovadas.")
        return redirect('detalhe_requisicao', requisicao_id=requisicao_id)

    try:
        requisicao.confirmar_transferencia()
        messages.success(request, "Transferência confirmada e estoque atualizado.")
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao confirmar a transferência: {e}")

    return redirect('detalhe_requisicao', requisicao_id=requisicao_id)

from django.views.generic import DetailView
from .models import Requisicao

class RequisicaoDetailView(DetailView):
    model = Requisicao
    template_name = 'estoque/detalhe_requisicao.html'
    context_object_name = 'requisicao'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['itens'] = self.object.itens.all()  # Supondo que 'itens' está relacionado à requisição
        return context

from django.shortcuts import render
from .models import Requisicao

def lista_requisicoes(request):
    requisicoes = Requisicao.objects.all()
    return render(request, 'requisicoes/lista_requisicoes.html', {'requisicoes': requisicoes})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import RequisicaoForm, ItemRequisicaoForm
from .models import Requisicao, ItemRequisicao

@login_required  # Assegure-se de que apenas usuários autenticados podem acessar essa view
def criar_requisicao(request):
    # Inicialize as variáveis
    requisicao = None  # Inicialize requisicao como None
    itens_requisicao = []  # Lista para armazenar itens da requisição

    if request.method == 'POST':
        form = RequisicaoForm(request.POST)
        item_form = ItemRequisicaoForm(request.POST)

        # Se o formulário principal for válido, salve a requisição
        if form.is_valid():
            requisicao = form.save(commit=False)
            requisicao.save()
            messages.success(request, "Requisição criada com sucesso.")

            # Se o botão "Adicionar Item" foi pressionado e o formulário de item é válido
            if 'add_item' in request.POST and item_form.is_valid():
                item = item_form.save(commit=False)
                item.requisicao = requisicao
                item.save()
                messages.success(request, "Item adicionado à requisição com sucesso.")
                return redirect('criar_requisicao')  # Redirecione para a mesma página para limpar os formulários

        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")

    else:
        form = RequisicaoForm()
        item_form = ItemRequisicaoForm()

    # Recupera os itens da requisição, se a requisição foi criada
    if requisicao:
        itens_requisicao = ItemRequisicao.objects.filter(requisicao=requisicao)

    return render(request, 'estoque/criar_requisicao.html', {
        'form': form,
        'item_form': item_form,
        'itens_requisicao': itens_requisicao,
    })
