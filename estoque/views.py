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
    Operador,
    Dispensacao,
    DistribuicaoMedicamento
)


from .forms import (
    MedicamentoForm,
    LoginForm,
    OperadorForm,
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

def lista_medicamentos(request):
    # Data atual
    now = timezone.now()
    # Data 3 meses à frente
    now_plus_3_months = (now + timedelta(days=90)).date()

    # Query para obter detalhes dos medicamentos com cálculo do valor total
    detalhes_medicamentos = (
        DetalhesMedicamento.objects.values(
            "medicamento__nome", "localizacao", "validade", "lote"
        )
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


def carregar_medicamentos_excel(request):
    # Diretório onde os arquivos Excel estão localizados
    excel_dir = os.path.join(settings.MEDIA_ROOT, "excel")
    excel_files = [
        "codigos_corretos.xlsx",
    ]

    for file_name in excel_files:
        file_path = os.path.join(excel_dir, file_name)
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            for index, row in df.iterrows():
                Medicamento.objects.update_or_create(
                    codigo_identificacao=row["Código"], defaults={"nome": row["Nome"]}
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
from django.forms import inlineformset_factory
from .models import EntradaEstoque, DetalhesMedicamento, Medicamento, Localizacao, Fabricante
from .forms import EntradaEstoqueForm, DetalhesMedicamentoForm
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DetalhesMedicamentoFormSet = inlineformset_factory(EntradaEstoque, DetalhesMedicamento, form=DetalhesMedicamentoForm, extra=1)

def entrada_estoque(request):
    if request.method == 'POST':
        form = EntradaEstoqueForm(request.POST)
        formset = DetalhesMedicamentoFormSet(request.POST, instance=EntradaEstoque())
        
        if form.is_valid() and formset.is_valid():
            entrada_estoque = form.save(commit=False)
            
            # Função para validar e converter datas
            def parse_date(date_str):
                try:
                    return datetime.strptime(date_str, '%d/%m/%Y').date()
                except ValueError as e:
                    logger.error(f"Erro ao converter data: {e}")
                    return None

            # Verificar e converter as datas
            entrada_estoque.data = parse_date(form.cleaned_data['data']) if isinstance(form.cleaned_data['data'], str) else form.cleaned_data['data']
            entrada_estoque.data_recebimento = parse_date(form.cleaned_data['data_recebimento']) if isinstance(form.cleaned_data['data_recebimento'], str) else form.cleaned_data['data_recebimento']
            
            if entrada_estoque.data is None or entrada_estoque.data_recebimento is None:
                logger.error("Data inválida fornecida")
                return render(request, 'estoque/entrada_estoque.html', {
                    'form': form,
                    'formset': formset,
                    'medicamentos_disponiveis': Medicamento.objects.all(),
                    'localizacoes_disponiveis': Localizacao.objects.all(),
                    'fabricantes_disponiveis': Fabricante.objects.all(),
                    'error_message': 'Data inválida fornecida. Por favor, corrija e tente novamente.'
                })
            
            entrada_estoque.save()
            formset.instance = entrada_estoque
            formset.save()
            return redirect('lista_medicamentos')
        else:
            logger.error("Form or formset is not valid")
            logger.error(f"Form errors: {form.errors}")
            logger.error(f"Formset errors: {formset.errors}")
            for form in formset:
                logger.error(f"Formset form errors: {form.errors}")
    else:
        form = EntradaEstoqueForm()
        formset = DetalhesMedicamentoFormSet(queryset=DetalhesMedicamento.objects.none())
    
    medicamentos_disponiveis = Medicamento.objects.all()
    localizacoes_disponiveis = Localizacao.objects.all()
    fabricantes_disponiveis = Fabricante.objects.all()
    
    return render(request, 'estoque/entrada_estoque.html', {
        'form': form,
        'formset': formset,
        'medicamentos_disponiveis': medicamentos_disponiveis,
        'localizacoes_disponiveis': localizacoes_disponiveis,
        'fabricantes_disponiveis': fabricantes_disponiveis,
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


def listar_operadores(request):
    operadores = Operador.objects.all()
    return render(request, "estoque/listar_operadores.html", {"operadores": operadores})


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
@login_required
def cadastrar_operador(request):
    if request.method == "POST":
        form = OperadorForm(request.POST)
        if form.is_valid():
            operador = form.save(commit=False)
            operador.save()
            form.save_m2m()
            messages.success(request, "Operador cadastrado com sucesso!")
            return redirect("cadastrar_operador")
    else:
        form = OperadorForm()
    return render(request, "estoque/cadastrar_operador.html", {"form": form})


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


def base(request):
    return render(request, "estoque/base.html")


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


def lotes_por_medicamento(request):
    medicamento_id = request.GET.get("medicamento_id")
    if medicamento_id:
        lotes = DetalhesMedicamento.objects.filter(
            medicamento_id=medicamento_id
        ).values("id", "lote")
        lotes_list = list(lotes)
        return JsonResponse({"lotes": lotes_list})
    return JsonResponse({"error": "Medicamento ID não fornecido"}, status=400)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from datetime import date
from .forms import SaidaEstoqueForm
from .models import SaidaEstoque, DetalhesMedicamento
from django.db.models import F

@login_required
@transaction.atomic
def saida_estoque(request):
    if request.method == "POST":
        form = SaidaEstoqueForm(request.POST)
        if form.is_valid():
            # Extração dos dados validados do formulário
            medicamento = form.cleaned_data["medicamento"]
            quantidade = form.cleaned_data["quantidade"]
            lote = form.cleaned_data["lote"]  # Obtem o objeto 'DetalhesMedicamento' selecionado no formulário
            departamento = form.cleaned_data["departamento"]  # Campo selecionado pelo usuário

            # Verificação para garantir que o lote é um objeto válido
            if not isinstance(lote, DetalhesMedicamento):
                messages.error(request, "O lote selecionado não é válido. Por favor, tente novamente.")
                return redirect("saida_estoque")

            # Verifica se há quantidade suficiente no lote selecionado
            if lote.quantidade >= quantidade:
                # Subtrai a quantidade desejada do estoque do lote
                lote.quantidade = F("quantidade") - quantidade
                lote.save()  # Salva as alterações no estoque do lote

                # Atualiza a instância do lote para obter a quantidade atualizada do banco de dados
                lote.refresh_from_db()

                # Cria o objeto de saída de estoque com os dados fornecidos
                saida = SaidaEstoque(
                    operador=request.user.username,
                    medicamento=medicamento,  # Usa o objeto medicamento selecionado no formulário
                    lote=lote,  # Lote associado ao medicamento
                    quantidade=quantidade,
                    departamento=departamento,  # Usa o departamento selecionado no formulário
                    data_atendimento=date.today(),  # Define a data de atendimento como hoje
                )
                saida.save()  # Salva a nova saída no banco de dados (UUID gerado automaticamente)

                # Exibe mensagem de sucesso e redireciona para a mesma página para nova retirada
                messages.success(
                    request,
                    f"Saída de estoque realizada com sucesso! Lote atualizado: {lote.lote} - Quantidade restante: {lote.quantidade}",
                )
                return redirect("saida_estoque")  # Redireciona para a mesma página para registrar outra saída
            else:
                # Caso a quantidade desejada seja maior que a disponível no lote
                messages.error(
                    request,
                    f"Quantidade insuficiente no lote selecionado ({lote.lote}). Quantidade disponível: {lote.quantidade}",
                )
        else:
            messages.error(
                request,
                "Erro ao validar o formulário. Por favor, revise os dados inseridos.",
            )
    else:
        # Inicializa um formulário vazio se o método não for POST
        form = SaidaEstoqueForm()

    # Renderiza o template com o formulário
    return render(request, "estoque/saida_estoque.html", {"form": form})

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
    DistribuicaoMedicamentoFormSet = modelformset_factory(DistribuicaoMedicamento, form=DistribuicaoMedicamentoForm, extra=3)

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
    distribuicoes = Distribuicao.objects.all()
    return render(request, 'estoque/consultar_distribuicoes.html', {'distribuicoes': distribuicoes})


