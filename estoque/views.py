from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Medicamento,DispensacaoMedicamento, Estoque,Paciente,Fornecedor,DetalhesMedicamento,Localizacao,Fabricante, Estabelecimento, Departamento, SaidaEstoque,Operador, Dispensacao
from .forms import MedicamentoForm, LoginForm, OperadorForm,PacienteForm,FornecedorForm,EstoqueForm, DetalhesMedicamentoFormSet,DetalhesMedicamentoForm,LocalizacaoForm,FabricanteForm, EstabelecimentoForm, DepartamentoForm,SaidaEstoqueForm, MedicoForm,DispensacaoForm, DispensacaoMedicamentoFormSet
from django.db.models import Sum
from django.utils import timezone
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

def lista_medicamentos(request):
    # Data atual
    now = timezone.now()
    # Data 3 meses à frente
    now_plus_3_months = (now + timedelta(days=90)).date()
    
    # Query para obter detalhes dos medicamentos
    detalhes_medicamentos = (
        DetalhesMedicamento.objects
        .values('medicamento__nome', 'localizacao', 'validade', 'lote')
        .annotate(total_quantidade=Sum('quantidade'), total_valor=Sum('valor'))
        .order_by('medicamento__nome')
    )
    
    return render(request, 'estoque/lista_medicamentos.html', {
        'detalhes_medicamentos': detalhes_medicamentos,
        'now_plus_3_months': now_plus_3_months,
    })

def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    query = request.GET.get('q')
    if query:
        pacientes = pacientes.filter(nome__icontains=query)
    return render(request, 'estoque/lista_pacientes.html', {'pacientes': pacientes})

@login_required
def novo_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'estoque/novo_paciente.html', {'form': form})

@login_required
def cadastro_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor cadastrado com sucesso.')
            return redirect('entrada_estoque')
        else:
            messages.error(request, 'Erro ao cadastrar fornecedor.')
    else:
        form = FornecedorForm()
    return render(request, 'estoque/cadastro_fornecedor.html', {'form': form})

@login_required
def cadastro_fabricante(request):
    if request.method == 'POST':
        form = FabricanteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fabricante cadastrado com sucesso.')
            return redirect('entrada_estoque')
        else:
            messages.error(request, 'Erro ao cadastrar fabricante.')
    else:
        form = FabricanteForm()
    return render(request, 'estoque/cadastro_fabricante.html', {'form': form})


def carregar_medicamentos_excel(request):
    # Diretório onde os arquivos Excel estão localizados
    excel_dir = os.path.join(settings.MEDIA_ROOT, 'excel')
    excel_files = [
        'codigos_corretos.xlsx',
    ]

    for file_name in excel_files:
        file_path = os.path.join(excel_dir, file_name)
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            for index, row in df.iterrows():
                Medicamento.objects.update_or_create(
                    codigo_identificacao=row['Código'],
                    defaults={'nome': row['Nome']}
                )

    return redirect('lista_medicamentos')

@login_required
def cadastrar_medicamento(request):
    medicamentos = Medicamento.objects.all()
    if request.method == 'POST':
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sucesso')  
    else:
        form = MedicamentoForm()
    return render(request, 'estoque/cadastrar_medicamento.html', {'form': form, 'medicamentos': medicamentos})


def sucesso(request):
    return render(request, 'estoque/sucesso.html')

@login_required
def cadastrar_localizacao(request):
    if request.method == 'POST':
        form = LocalizacaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Localização cadastrada com sucesso.')
            return redirect('lista_localizacoes')
        else:
            messages.error(request, 'Erro ao cadastrar localização.')
    else:
        form = LocalizacaoForm()
    return render(request, 'estoque/cadastrar_localizacao.html', {'form': form})

def lista_localizacoes(request):
    localizacoes = Localizacao.objects.all()
    return render(request, 'estoque/lista_localizacoes.html', {'localizacoes': localizacoes})

@login_required
def entrada_estoque(request):
    if request.method == 'POST':
        form = EstoqueForm(request.POST)
        formset = DetalhesMedicamentoFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            estoque = form.save()
            formset.instance = estoque
            formset.save()
            messages.success(request, 'Entrada de medicamento registrada com sucesso.')
            return redirect('entrada_estoque')
        else:
            print(form.errors)
            print(formset.errors)
            messages.error(request, 'Erro ao registrar entrada de medicamento.')
    else:
        form = EstoqueForm()
        formset = DetalhesMedicamentoFormSet()

    fabricantes = Fabricante.objects.all()  # Recuperando todos os fabricantes do banco de dados
    context = {
        'form': form,
        'formset': formset,
        'fabricantes': fabricantes
    }
    return render(request, 'estoque/entrada_estoque.html', context)

@login_required
def cadastrar_estabelecimento(request):
    if request.method == 'POST':
        form = EstabelecimentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estabelecimento cadastrado com sucesso.')
            return redirect('lista_estabelecimentos')
        else:
            messages.error(request, 'Erro ao cadastrar estabelecimento.')
    else:
        form = EstabelecimentoForm()
    return render(request, 'estoque/cadastrar_estabelecimento.html', {'form': form})


def lista_estabelecimentos(request):
    estabelecimentos = Estabelecimento.objects.all()
    return render(request, 'estoque/lista_estabelecimentos.html', {'estabelecimentos': estabelecimentos})

@login_required
def cadastrar_departamento(request):
    if request.method == 'POST':
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento cadastrado com sucesso.')
            return redirect('lista_departamento')
        else:
            messages.error(request, 'Erro ao cadastrar departamento.')
    else:
        form = DepartamentoForm()
    return render(request, 'estoque/cadastrar_departamento.html', {'form': form})

def lista_departamento(request):
    departamentos = Departamento.objects.all()
    return render(request, 'estoque/lista_departamento.html', {'departamentos': departamentos})


def listar_operadores(request):
    operadores = Operador.objects.all()
    return render(request, 'estoque/listar_operadores.html', {'operadores': operadores})

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
@login_required
def cadastrar_operador(request):
    if request.method == 'POST':
        form = OperadorForm(request.POST)
        if form.is_valid():
            operador = form.save(commit=False)
            operador.save()
            form.save_m2m()
            messages.success(request, 'Operador cadastrado com sucesso!')
            return redirect('cadastrar_operador')
    else:
        form = OperadorForm()
    return render(request, 'estoque/cadastrar_operador.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['operador'], password=form.cleaned_data['senha'])
            if user is not None: 
                login(request, user)
                return redirect('estoque/base')
            else:
                messages.error(request, 'Operador inválido')
    else:
        form = LoginForm()
    return render(request, 'estoque/login.html', {'form': form})

def base(request):
    return render(request, 'estoque/base.html') 

@login_required
def cadastrar_medico(request):
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Médico cadastrado com sucesso!')
            return redirect('cadastrar_medico')  # Redirect to avoid form resubmission
    else:
        form = MedicoForm()

    return render(request, 'estoque/cadastrar_medico.html', {'form': form})

def listar_dispensacoes(request):
    dispensacoes = Dispensacao.objects.all()
    return render(request, 'estoque/listar_dispensacoes.html', {'dispensacoes': dispensacoes})

@login_required
def nova_dispensacao(request):
    if request.method == 'POST':
        form = DispensacaoForm(request.POST)
        formset = DispensacaoMedicamentoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            dispensacao = form.save()
            medicamentos = formset.save(commit=False)
            for medicamento in medicamentos:
                medicamento.dispensacao = dispensacao
                medicamento.save()
            messages.success(request, 'Dispensação registrada com sucesso!')
            return redirect('listar_dispensacoes')
    else:
        medicamentos_com_estoque = Medicamento.objects.filter(detalhesmedicamento__quantidade__gt=0).distinct()
    
    form = DispensacaoForm()
    formset = DispensacaoMedicamentoFormSet(queryset=DispensacaoMedicamento.objects.none())
    
    # Obter dispensações recentes
    dispensacoes_recentes = Dispensacao.objects.all().order_by('-data_dispensacao')[:3]

    return render(request, 'estoque/nova_dispensacao.html', {
        'form': form,
        'formset': formset,
        'medicamentos_disponiveis': medicamentos_com_estoque,
        'dispensacoes_recentes': dispensacoes_recentes,
    })

def detalhes_dispensacao(request, id):
    dispensacao = get_object_or_404(Dispensacao, id=id)
    return render(request, 'estoque/detalhes_dispensacao.html', {'dispensacao': dispensacao})

@login_required
def saida_estoque(request):
    SaidaEstoqueFormSet = formset_factory(SaidaEstoqueForm, extra=1)  # Definindo o formset
    
    if request.method == 'POST':
        formset = SaidaEstoqueFormSet(request.POST)  # Formset para múltiplos medicamentos
        if formset.is_valid():
            for form in formset:
                medicamento = form.cleaned_data.get('medicamento')
                quantidade = form.cleaned_data.get('quantidade')
                lote = form.cleaned_data.get('lote')

                # Atualizar o estoque do lote selecionado
                if lote and lote.quantidade >= quantidade:
                    lote.quantidade -= quantidade
                    lote.save()

            messages.success(request, 'Saída de estoque realizada com sucesso!')
            return redirect('sucesso')
        else:
            messages.error(request, 'Formulário inválido. Verifique os dados inseridos.')
    else:
        formset = SaidaEstoqueFormSet()

    return render(request, 'estoque/saida_estoque.html', {'formset': formset})

@login_required
def get_lotes(request):
    medicamento_id = request.GET.get('medicamento_id')
    if medicamento_id:
        lotes = DetalhesMedicamento.objects.filter(medicamento_id=medicamento_id).values('id', 'lote')
        seen_lotes = set()
        unique_lotes = []
        
        for lote in lotes:
            if lote['lote'] not in seen_lotes:
                seen_lotes.add(lote['lote'])
                unique_lotes.append(lote)
        
        return JsonResponse({'lotes': unique_lotes})
    return JsonResponse({'error': 'Medicamento ID não fornecido'}, status=400)

def lotes_por_medicamento(request):
    medicamento_id = request.GET.get('medicamento_id')
    if medicamento_id:
        lotes = DetalhesMedicamento.objects.filter(medicamento_id=medicamento_id).values('id', 'lote')
        lotes_list = list(lotes)
        return JsonResponse({'lotes': lotes_list})
    return JsonResponse({'error': 'Medicamento ID não fornecido'}, status=400)