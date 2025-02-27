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


def base(request):
    return render(request, "estoque/base.html")  
    

from django.db.models import Sum, F, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import DetalhesMedicamento, Estoque

@login_required
def lista_medicamentos(request):
    now = timezone.now()
    now_plus_3_months = (now + timedelta(days=90)).date()

    estabelecimento = request.user.profile.estabelecimento

    estoques = Estoque.objects.filter(estabelecimento=estabelecimento).values(
        "medicamento__id", "medicamento__nome"
    ).annotate(
        quantidade_em_estoque=Sum("quantidade")
    )

    detalhes_medicamentos = list(DetalhesMedicamento.objects.filter(
        Q(estoque__estabelecimento=estabelecimento) | Q(estoque__estabelecimento__isnull=True)
    ).values(
        "medicamento__id", "medicamento__nome", "localizacao", "validade", "lote", "fabricante"
    ).annotate(
        total_quantidade=Sum("quantidade"),
        total_valor=Sum(F("quantidade") * F("valor"))
    ).order_by("medicamento__nome", "lote"))

    estoque_dict = {item["medicamento__id"]: item["quantidade_em_estoque"] for item in estoques}

    for item in detalhes_medicamentos:
        item["quantidade_em_estoque"] = estoque_dict.get(item["medicamento__id"], 0)

    medicamentos_no_detalhes = {item["medicamento__id"] for item in detalhes_medicamentos}

    for item in estoques:
        if item["medicamento__id"] not in medicamentos_no_detalhes:
            # Buscar lote e validade mais recente no DetalhesMedicamento
            detalhe = DetalhesMedicamento.objects.filter(
                medicamento_id=item["medicamento__id"],
                estoque__estabelecimento=estabelecimento
            ).order_by("-validade").first()  # Ordena do mais recente para o mais antigo

            detalhes_medicamentos.append({
                "medicamento__id": item["medicamento__id"],
                "medicamento__nome": item["medicamento__nome"],
                "localizacao": detalhe.localizacao if detalhe else "N/A",
                "validade": detalhe.validade if detalhe else "N/A",
                "lote": detalhe.lote if detalhe else "N/A",
                "fabricante":detalhe.fabricante if detalhe else "N/A",
                "total_quantidade": 0,
                "total_valor": 0,
                "quantidade_em_estoque": item["quantidade_em_estoque"]
            })

    total_valor_geral = sum(item["total_valor"] or 0 for item in detalhes_medicamentos)

    return render(
        request,
        "estoque/lista_medicamentos.html",
        {
            "detalhes_medicamentos": detalhes_medicamentos,
            "now_plus_3_months": now_plus_3_months,
            "total_valor_geral": total_valor_geral,
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
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from .forms import EntradaEstoqueForm, DetalhesMedicamentoFormSet
from .models import EntradaEstoque, Estoque

@login_required
def entrada_estoque(request):
    if request.method == 'POST':
        form = EntradaEstoqueForm(request.POST, user=request.user)
        formset = DetalhesMedicamentoFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                entrada = form.save(commit=False)
                entrada.user = request.user
                entrada.save()

                detalhes = formset.save(commit=False)
                for detalhe in detalhes:
                    detalhe.entrada = entrada
                    detalhe.estabelecimento = entrada.estabelecimento  

                    estoque, created = Estoque.objects.get_or_create(
                        medicamento=detalhe.medicamento,
                        estabelecimento=entrada.estabelecimento,
                        defaults={'quantidade': detalhe.quantidade}
                    )

                    if not created:
                        estoque.quantidade += detalhe.quantidade
                        estoque.save()

                    detalhe.estoque = estoque
                    detalhe.save()

                messages.success(request, 'Entrada de medicamentos concluída com sucesso.')
                return redirect('sucesso')  # Substitua por uma URL válida
    else:
        form = EntradaEstoqueForm(user=request.user)  # Passa o usuário corretamente
        formset = DetalhesMedicamentoFormSet()  # Garante que o formset seja criado corretamente

    return render(request, 'estoque/entrada_estoque.html', {
        'entrada_form': form,
        'detalhes_formset': formset,
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

from django.utils.safestring import mark_safe
import json
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import (
    Dispensacao, DispensacaoMedicamento, DetalhesMedicamento, Medicamento, Estoque
)
from .forms import DispensacaoForm, DispensacaoMedicamentoFormSet

@login_required
def nova_dispensacao(request):
    usuario = request.user  # Obtém o usuário logado

    # Verifica se o usuário tem um perfil associado a um estabelecimento
    try:
        estabelecimento = usuario.profile.estabelecimento
    except AttributeError:
        messages.error(request, "Seu usuário não está associado a um estabelecimento.")
        return redirect("listar_dispensacoes")

    if request.method == "POST":
        form = DispensacaoForm(request.POST)
        formset = DispensacaoMedicamentoFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():  # Garante que todas as operações sejam concluídas corretamente
                dispensacao = form.save(commit=False)
                dispensacao.usuario = usuario  # Registra o usuário que fez a dispensação
                dispensacao.save()
                
                medicamentos = formset.save(commit=False)

                for medicamento in medicamentos:
                    medicamento.dispensacao = dispensacao

                    # Buscar o estoque geral do medicamento no estabelecimento do usuário
                    try:
                        estoque = Estoque.objects.get(
                            medicamento=medicamento.medicamento, estabelecimento=estabelecimento
                        )
                    except Estoque.DoesNotExist:
                        messages.error(request, f"Estoque não encontrado para {medicamento.medicamento} no {estabelecimento}!")
                        return redirect("nova_dispensacao")

                    # Verificar se há quantidade suficiente no estoque total
                    if estoque.quantidade < medicamento.quantidade:
                        messages.error(request, f"Estoque insuficiente para {medicamento.medicamento}!")
                        return redirect("nova_dispensacao")

                    # Atualizar o estoque total do estabelecimento
                    estoque.quantidade -= medicamento.quantidade
                    estoque.save()

                    # Atualizar os lotes, priorizando os mais antigos
                    detalhes_estoque = DetalhesMedicamento.objects.filter(
                        medicamento=medicamento.medicamento,
                        quantidade__gt=0,
                        estabelecimento=estabelecimento  # Filtra pelo mesmo estabelecimento
                    ).order_by("validade")  # Usa os lotes mais antigos primeiro

                    quantidade_a_reduzir = medicamento.quantidade

                    for lote in detalhes_estoque:
                        if quantidade_a_reduzir <= 0:
                            break  # Se toda a quantidade já foi retirada, sai do loop

                        if lote.quantidade >= quantidade_a_reduzir:
                            lote.quantidade -= quantidade_a_reduzir
                            lote.save()
                            quantidade_a_reduzir = 0
                        else:
                            quantidade_a_reduzir -= lote.quantidade
                            lote.quantidade = 0
                            lote.save()

                    medicamento.save()  # Salva a dispensação após a atualização do estoque

                messages.success(request, "Dispensação registrada e estoque atualizado com sucesso!")
                return redirect("listar_dispensacoes")

    else:
        medicamentos_com_estoque = Medicamento.objects.filter(
            estoques_medicamento__quantidade__gt=0,  # Busca medicamentos disponíveis no estoque geral
            estoques_medicamento__estabelecimento=estabelecimento,  # Apenas do estabelecimento do usuário
        ).distinct()

    form = DispensacaoForm()
    formset = DispensacaoMedicamentoFormSet(queryset=DispensacaoMedicamento.objects.none())

    # Convertendo medicamentos para JSON para uso no JavaScript
    medicamentos_json = json.dumps(
        [{"id": med.id, "nome": med.nome} for med in medicamentos_com_estoque]
    )

    dispensacoes_recentes = Dispensacao.objects.all().order_by("-data_dispensacao")[:3]

    
    return render(
        request,
        "estoque/nova_dispensacao.html",
        {
            "form": form,
            "formset": formset,
            "medicamentos_disponiveis": mark_safe(medicamentos_json),
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
from django.shortcuts import get_object_or_404
from .models import DetalhesMedicamento, Medicamento

def lotes_por_medicamento(request, medicamento_id):
    """
    Retorna os lotes disponíveis para o medicamento selecionado,
    filtrados pelo estabelecimento do usuário logado.
    """
    user = request.user

    # Verificar se o usuário tem um estabelecimento associado
    if not hasattr(user, 'profile') or not user.profile.estabelecimento:
        return JsonResponse({"error": "Usuário não possui um estabelecimento associado."}, status=400)

    estabelecimento = user.profile.estabelecimento

    # Obter o medicamento selecionado
    medicamento = get_object_or_404(Medicamento, id=medicamento_id)

    # Filtrar lotes disponíveis no estabelecimento do usuário
    lotes = DetalhesMedicamento.objects.filter(
        medicamento=medicamento,
        estabelecimento=estabelecimento,
        quantidade__gt=0  # Apenas lotes com quantidade disponível
    )

    # Debugging: Imprimir lotes filtrados no terminal
    print(f"Usuário: {user.username} | Estabelecimento: {estabelecimento}")
    print(f"Medicamento: {medicamento.nome} (ID: {medicamento.id})")
    print(f"Lotes encontrados: {list(lotes.values('id', 'lote', 'quantidade', 'estabelecimento_id'))}")

    # Verificar se há lotes disponíveis
    if not lotes.exists():
        return JsonResponse({"message": "Nenhum lote disponível para este medicamento."}, status=404)

    # Construir a resposta JSON
    data = [
        {"id": lote.id, "codigo": lote.lote, "quantidade": lote.quantidade}
        for lote in lotes
    ]
    return JsonResponse(data, safe=False)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SaidaEstoqueForm
from .models import DetalhesMedicamento, Estoque
from django.utils.timezone import now

from django.db import transaction

@login_required
def saida_estoque(request):
    if request.method == 'POST':
        form = SaidaEstoqueForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():  # Garante que todas as operações sejam atômicas
                saida = form.save(commit=False)
                saida.data_atendimento = now()  # Define a data/hora atual
                saida.user = request.user.username

                lote = saida.lote

                # Verificar se o lote pertence ao estabelecimento do usuário
                if lote.estabelecimento != request.user.profile.estabelecimento:
                    messages.error(request, "O lote selecionado não pertence ao seu estabelecimento.")
                    return redirect('saida_estoque')

                # Verificar se há quantidade suficiente no lote
                if lote.quantidade < saida.quantidade:
                    messages.error(request, "Quantidade insuficiente no lote selecionado.")
                    return redirect('saida_estoque')

                # Atualizar a quantidade no lote
                lote.quantidade -= saida.quantidade
                lote.save()

                # Atualizar o estoque geral do estabelecimento
                try:
                    estoque = Estoque.objects.get(
                        estabelecimento=request.user.profile.estabelecimento,
                        medicamento=saida.medicamento,
                    )
                    if estoque.quantidade < saida.quantidade:
                        messages.error(request, "Estoque insuficiente no estabelecimento.")
                        return redirect('saida_estoque')

                    estoque.quantidade -= saida.quantidade
                    estoque.save()
                except Estoque.DoesNotExist:
                    messages.error(request, "Estoque não encontrado para este medicamento no estabelecimento.")
                    return redirect('saida_estoque')

                # Salvar a saída
                saida.save()

                messages.success(request, "Saída registrada com sucesso!")
                return redirect('saida_estoque')
    else:
        form = SaidaEstoqueForm(user=request.user)

    return render(request, 'estoque/saida_estoque.html', {'form': form})



from django.http import JsonResponse
from .models import DetalhesMedicamento

def get_lotes(request, medicamento_id):
    lotes = DetalhesMedicamento.objects.filter(
        medicamento_id=medicamento_id, quantidade__gt=0
    ).values("id", "lote")
    return JsonResponse({"lotes": list(lotes)})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DetalhesMedicamento, DistribuicaoMedicamento
from .forms import DistribuicaoMedicamentoForm

@login_required
def distribuicao_sem_requisicao(request):
    user_profile = request.user.profile
    estabelecimento_origem = user_profile.estabelecimento

    if not estabelecimento_origem:
        messages.error(request, "Você não está associado a nenhum estabelecimento.")
        return redirect('dashboard')

    if request.method == "POST":
        form = DistribuicaoMedicamentoForm(request.POST, estabelecimento_origem=estabelecimento_origem)
        if form.is_valid():
            # Dados do formulário
            medicamento = form.cleaned_data['medicamento']
            lote = form.cleaned_data['lote']
            quantidade = form.cleaned_data['quantidade']
            estabelecimento_destino = form.cleaned_data['estabelecimento_destino']

            # Verificar estoque no estabelecimento de origem
            detalhes_medicamento = get_object_or_404(
                DetalhesMedicamento,
                medicamento=medicamento,
                lote=lote.lote,
                estabelecimento=estabelecimento_origem
            )

            if detalhes_medicamento.quantidade < quantidade:
                messages.error(request, "Quantidade insuficiente no estoque.")
                return redirect('distribuicao_sem_requisicao')

            # Atualizar o estoque no estabelecimento de origem
            detalhes_medicamento.quantidade -= quantidade
            detalhes_medicamento.save()

            # Atualizar ou criar o estoque no estabelecimento de destino
            detalhes_destino, created = DetalhesMedicamento.objects.get_or_create(
                medicamento=medicamento,
                lote=lote.lote,
                estabelecimento=estabelecimento_destino,
                defaults={
                    'quantidade': 0,
                    'validade': lote.validade,
                    'localizacao': lote.localizacao,
                    'fabricante': lote.fabricante,
                    'valor': lote.valor,
                }
            )
            detalhes_destino.quantidade += quantidade
            detalhes_destino.save()

            # Registrar a distribuição
            DistribuicaoMedicamento.objects.create(
                
                
                medicamento=medicamento,
                lote=detalhes_medicamento,
                quantidade=quantidade,
               
            )

            messages.success(request, "Distribuição realizada com sucesso!")
            return redirect('estoque')
    else:
        form = DistribuicaoMedicamentoForm(estabelecimento_origem=estabelecimento_origem)

    return render(request, 'estoque/distribuicao_sem_requisicao.html', {'form': form})



from django.shortcuts import render
from .models import Distribuicao

def consultar_distribuicoes(request):
    distribuicoes = Distribuicao.objects.all().order_by('-data_atendimento')
    return render(request, 'estoque/consultar_distribuicoes.html', {'distribuicoes': distribuicoes})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Distribuicao, DistribuicaoMedicamento, DetalhesMedicamento, Estoque, Estabelecimento
from .forms import DistribuicaoForm, DistribuicaoMedicamentoForm
from django.forms import inlineformset_factory
from django.db import transaction

@login_required
def distribuicao_sem_requisicao(request):
    user_estabelecimento = request.user.profile.estabelecimento

    DistribuicaoMedicamentoFormSet = inlineformset_factory(
        Distribuicao,
        DistribuicaoMedicamento,
        form=DistribuicaoMedicamentoForm,
        extra=1,
        can_delete=True
    )

    distrib = Distribuicao(estabelecimento_origem=user_estabelecimento)
    distrib_form = DistribuicaoForm(request.POST or None, user_estabelecimento=user_estabelecimento)
    formset = DistribuicaoMedicamentoFormSet(
        request.POST or None,
        instance=distrib,
        form_kwargs={'distrib': distrib}
    )
    
    formset = DistribuicaoMedicamentoFormSet(
    request.POST or None,
    instance=distrib,
    form_kwargs={'distrib': distrib}
)
    if request.method == 'POST':
        if distrib_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                distrib = distrib_form.save(commit=False)
                distrib.estabelecimento_origem = user_estabelecimento
                distrib.save()

                medicamentos = formset.save(commit=False)
                for medicamento in medicamentos:
                    medicamento.distribuicao = distrib

                    # Atualiza o estoque do lote
                    lote = medicamento.lote
                    if medicamento.quantidade > lote.quantidade:
                        raise ValueError("Quantidade maior que o estoque disponível no lote.")

                    lote.quantidade -= medicamento.quantidade
                    lote.save()
                    medicamento.save()

            return redirect('lista_distribuicoes')

    context = {
        'distrib_form': distrib_form,
        'formset': formset,
    }
    return render(request, 'estoque/distribuicao_sem_requisicao.html', context)


def lista_distribuicoes(request):
    distribuicoes = Distribuicao.objects.all()
    return render(request, 'estoque/lista_distribuicoes.html', {'distribuicoes': distribuicoes})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from .models import Requisicao, ItemRequisicao
from .forms import RequisicaoForm, ItemRequisicaoForm

@login_required
def criar_requisicao(request):
    ItemRequisicaoFormSet = inlineformset_factory(
        Requisicao, ItemRequisicao,
        form=ItemRequisicaoForm,  
        extra=1, can_delete=True
    )

    if request.method == "POST":
        form = RequisicaoForm(request.POST)
        formset = ItemRequisicaoFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            requisicao = form.save(commit=False)  # Criar a requisição sem salvar ainda

            # Definir o estabelecimento de origem como o do usuário logado
            if hasattr(request.user, 'profile') and request.user.profile.estabelecimento:
                requisicao.estabelecimento_origem = request.user.profile.estabelecimento
            else:
                messages.error(request, "Você não tem um estabelecimento associado.")
                return redirect('criar_requisicao')

            requisicao.save()  # Agora salva a requisição no banco
           
            formset.instance = requisicao  # Associa os itens à requisição salva
            formset.save()  # Agora pode salvar os itens

            messages.success(request, "Requisição criada com sucesso!")
            return redirect('listar_requisicoes')  # Redireciona para a lista de requisições

    else:
        form = RequisicaoForm()
        formset = ItemRequisicaoFormSet()

    return render(request, 'estoque/criar_requisicao.html', {'form': form, 'formset': formset})



# Listar requisições pendentes para o estabelecimento de destino
@login_required
def listar_requisicoes(request):
    estabelecimento = request.user.profile.estabelecimento
    requisicoes = Requisicao.objects.filter(estabelecimento_destino=estabelecimento, status='Pendente')
    return render(request, 'estoque/listar_requisicoes.html', {'requisicoes': requisicoes})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from estoque.models import Requisicao, DetalhesMedicamento

@login_required
def responder_requisicao(request, requisicao_id):
    requisicao = get_object_or_404(Requisicao, id=requisicao_id)
    itens_requisicao = requisicao.itens.all()

    # Criando um dicionário para armazenar os lotes disponíveis para cada medicamento
    lotes_disponiveis = {}
    for item in itens_requisicao:
        lotes = DetalhesMedicamento.objects.filter(
            medicamento=item.medicamento,
            estabelecimento=requisicao.estabelecimento_destino, 
            quantidade__gt=0  # Apenas lotes com quantidade disponível
        ).order_by("validade")  # Ordenando por validade mais curta
        lotes_disponiveis[item.medicamento.id] = lotes

    if request.method == "POST":
        for item in itens_requisicao:
            lote_id = request.POST.get(f'form-{item.id}-lote')
            quantidade_enviada = int(request.POST.get(f'form-{item.id}-quantidade', 0))

            print(f"Lote selecionado para {item.medicamento.nome}: {lote_id}")  # DEBUG

            if not lote_id:
                messages.error(request, f"O item {item.medicamento.nome} não possui um lote selecionado!")
                return redirect('responder_requisicao', requisicao_id=requisicao.id)

            # 🔎 Depuração: Verificar se o lote existe antes de aplicar o filtro de estabelecimento
            try:
                lote = DetalhesMedicamento.objects.get(id=lote_id)
            except DetalhesMedicamento.DoesNotExist:
                messages.error(request, f"Lote {lote_id} não encontrado para o medicamento {item.medicamento.nome}.")
                return redirect('responder_requisicao', requisicao_id=requisicao.id)

            # 🔍 Verificar se o lote pertence ao estabelecimento correto
            if lote.estabelecimento != requisicao.estabelecimento_destino:
                messages.error(
                    request, 
                    f"O lote {lote.lote} do medicamento {item.medicamento.nome} pertence ao estabelecimento de origem."
                )
                return redirect('responder_requisicao', requisicao_id=requisicao.id)

            # 📉 Verificar se há estoque suficiente
            if quantidade_enviada > lote.quantidade:
                messages.error(request, f"Estoque insuficiente para {item.medicamento.nome} (Lote {lote.codigo})!")
                return redirect('responder_requisicao', requisicao_id=requisicao.id)

            # ✅ Atualizando os registros
            lote.quantidade -= quantidade_enviada
            lote.save()

            # Subtrair a quantidade no Estoque (modelo Estoque)
            estoque_destino = Estoque.objects.get(
                estabelecimento=requisicao.estabelecimento_destino,
                medicamento=item.medicamento
            )
            estoque_destino.quantidade -= quantidade_enviada  
            estoque_destino.save()

            # Criando ou atualizando o estoque no DetalhesMedicamento (modelo DetalhesMedicamento)
            estoque_destino_detalhes, created = DetalhesMedicamento.objects.get_or_create(
                medicamento=item.medicamento,
                lote=lote.lote,
                estabelecimento=requisicao.estabelecimento_destino,
                defaults={'quantidade': 0, 'validade': lote.validade, 'valor':lote.valor}
            )

            # Atualiza a quantidade do DetalhesMedicamento no estabelecimento de destino
            estoque_destino_detalhes.quantidade == quantidade_enviada
            if not estoque_destino_detalhes.valor:
                estoque_destino_detalhes.valor = lote.valor
            estoque_destino_detalhes.save()

            # Atualiza os itens da requisição com a quantidade enviada
            item.lote = lote
            item.quantidade_enviada = quantidade_enviada
            item.save()

        # Atualiza o status da requisição
        requisicao.status = 'Aprovada'
        requisicao.save()

        messages.success(request, "Medicamentos enviados com sucesso!")
        return redirect('listar_requisicoes')  # Redirecionando após salvar

    # Retorna o formulário se não for POST
    return render(request, "estoque/responder_requisicao.html", {
        "requisicao": requisicao,
        "itens_requisicao": itens_requisicao,
        "lotes_disponiveis": lotes_disponiveis
    })


    


from django.http import JsonResponse
from .models import Estoque, Medicamento

@login_required
def medicamentos_por_estabelecimento(request, estabelecimento_id):
    medicamentos = Medicamento.objects.filter(
    estoques_medicamento__estabelecimento_id=estabelecimento_id
).distinct().values("id", "nome")
    return JsonResponse(list(medicamentos), safe=False)


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Requisicao, Estoque, DetalhesMedicamento

@login_required
def confirmar_requisicao(request, pk):
    requisicao = get_object_or_404(Requisicao, pk=pk)  # Apenas o 'pk' é necessário aqui
    itens = ItemRequisicao.objects.filter(requisicao=requisicao)

    if requisicao.status != "Aprovada":
        messages.error(request, "A requisição precisa estar aprovada antes de ser confirmada.")
        return redirect('listar_requisicoes')

    try:
        with transaction.atomic():
            for item in requisicao.itens.all():
                if not item.lote:
                    messages.error(request, f"O item {item.medicamento.nome} não possui um lote selecionado!")
                    return redirect('listar_requisicoes')  

                # Criar ou obter o estoque no estabelecimento de origem
                estoque, created = Estoque.objects.get_or_create(
                    estabelecimento=requisicao.estabelecimento_origem,
                    medicamento=item.medicamento,
                    defaults={'quantidade': 0}
                )

                # Criar ou atualizar o estoque detalhado (DetalhesMedicamento)
                detalhes_medicamento, created = DetalhesMedicamento.objects.get_or_create(
                    medicamento=item.medicamento,
                    lote=item.lote.lote,
                    estabelecimento=requisicao.estabelecimento_origem,
                    defaults={
                        'quantidade': 0, 
                        'validade': item.lote.validade, 
                        'estoque': estoque  # ✅ Vincular corretamente ao estoque
                    }
                )

                # Atualizar a quantidade no estoque detalhado
                detalhes_medicamento.quantidade += item.quantidade
                detalhes_medicamento.estoque = estoque  # ✅ Garantir que está vinculado ao estoque correto
                detalhes_medicamento.save()

                # Atualizar a quantidade do estoque geral
                estoque.quantidade += item.quantidade
                estoque.save()

            # Atualizar status da requisição
            requisicao.status = "Concluída"
            requisicao.save()

            messages.success(request, "Requisição confirmada e estoque atualizado com sucesso!")
            return redirect('listar_requisicoes')

    except ValidationError as e:
        messages.error(request, f"Erro na confirmação: {str(e)}")
        return redirect('listar_requisicoes')




from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Requisicao

@login_required
def receber_requisicoes(request):
    """Lista as requisições que estão prontas para serem recebidas pelo estabelecimento do usuário logado."""
    estabelecimento_usuario = request.user.profile.estabelecimento

    requisicoes_pendentes = Requisicao.objects.filter(
        estabelecimento_origem=estabelecimento_usuario,
        status__in=["Aprovada", "Processando Transferência"]  # Agora filtra múltiplos status
    )

    return render(request, "estoque/receber_requisicoes.html", {"requisicoes": requisicoes_pendentes})


