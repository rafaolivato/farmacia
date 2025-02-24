from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import  Distribuicao,Estoque,Localizacao, DistribuicaoMedicamento,SaidaEstoque,Departamento,Dispensacao, DispensacaoMedicamento,Medicamento, EntradaEstoque, Paciente, Fornecedor, DetalhesMedicamento, Estabelecimento, Fabricante

class DistribuicaoMedicamentoInline(admin.TabularInline):
    model = DistribuicaoMedicamento
    extra = 1

class DistribuicaoAdmin(admin.ModelAdmin):
    inlines = [DistribuicaoMedicamentoInline]
    list_display = ('estabelecimento_origem', 'estabelecimento_destino', 'data_atendimento')


admin.site.register(Medicamento)
admin.site.register(EntradaEstoque)
admin.site.register(Paciente)
admin.site.register(Fornecedor)
admin.site.register(DetalhesMedicamento)
admin.site.register(Fabricante)
admin.site.register(Estabelecimento)
admin.site.register(Departamento)
admin.site.register(SaidaEstoque)
admin.site.register(Distribuicao, DistribuicaoAdmin)
admin.site.register(DistribuicaoMedicamento)
admin.site.register(Estoque)
admin.site.register(Localizacao)


# Crie um Inline para DispensacaoMedicamento
class DispensacaoMedicamentoInline(admin.TabularInline):
    model = DispensacaoMedicamento
    extra = 1  # Número de formulários em branco exibidos para adicionar novos medicamentos
    min_num = 1  # Número mínimo de medicamentos por dispensação
    can_delete = True  # Permite excluir medicamentos
    verbose_name = "Medicamento"
    verbose_name_plural = "Medicamentos"

# Customize a interface de Dispensacao no admin
@admin.register(Dispensacao)
class DispensacaoAdmin(admin.ModelAdmin):
    inlines = [DispensacaoMedicamentoInline]
    list_display = ['id', 'paciente', 'data_dispensacao']  # Customize o que aparecerá na lista de dispensações
    search_fields = ['paciente', 'data_dispensacao']  # Campos que você pode buscar no admin

# Registrar DispensacaoMedicamento de forma independente também, se quiser
@admin.register(DispensacaoMedicamento)
class DispensacaoMedicamentoAdmin(admin.ModelAdmin):
    list_display = ['dispensacao', 'medicamento', 'quantidade']
    search_fields = ['medicamento__nome', 'dispensacao__paciente']

# admin.py
from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'estabelecimento')
    list_filter = ('estabelecimento',)

from django.contrib import admin
from .models import Requisicao, ItemRequisicao
from django.utils.timezone import now

@admin.register(Requisicao)
class RequisicaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'estabelecimento_origem', 'estabelecimento_destino', 'status', 'data_requisicao', 'usuario_aprovador')
    list_filter = ('status', 'data_requisicao')
    search_fields = ('estabelecimento_origem__nome', 'estabelecimento_destino__nome', 'usuario_aprovador__username')
    actions = ['aprovar_requisicao']

    def aprovar_requisicao(self, request, queryset):
        """Ação para aprovar requisições em massa no Django Admin."""
        for requisicao in queryset:
            if requisicao.status != "Pendente":
                self.message_user(request, f"A requisição {requisicao.id} já foi processada.", level='error')
                continue

            requisicao.usuario_aprovador = request.user  # Define o usuário logado como aprovador
            requisicao.status = "Aprovada"
            requisicao.data_aprovacao = now().date()
            requisicao.save()

            self.message_user(request, f"A requisição {requisicao.id} foi aprovada com sucesso.", level='success')

    aprovar_requisicao.short_description = "Aprovar requisição selecionada"

@admin.register(ItemRequisicao)
class ItemRequisicaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'requisicao', 'medicamento', 'quantidade', 'lote')
    search_fields = ('medicamento__nome', 'lote__lote')  # 🔹 Adicionado para evitar erro

class ItemRequisicaoInline(admin.TabularInline):
    model = ItemRequisicao
    extra = 1
    autocomplete_fields = ['medicamento', 'lote']
    search_fields = ['medicamento__nome', 'lote__lote']  # 🔹 Adicionado para evitar erro


