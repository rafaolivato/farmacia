from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import  Distribuicao, DistribuicaoMedicamento,SaidaEstoque,Departamento,Dispensacao, DispensacaoMedicamento,Medicamento, EntradaEstoque, Paciente, Funcionalidade, Fornecedor, DetalhesMedicamento, PerfilOperador, Operador, Estabelecimento, Fabricante

# Defina a classe OperadorAdmin
class OperadorAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('nome_completo', 'cpf', 'email')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
        ('Perfil', {'fields': ('perfil', 'estabelecimentos')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nome_completo', 'cpf', 'email', 'password1', 'password2'),
        }),
    )


class DistribuicaoMedicamentoInline(admin.TabularInline):
    model = DistribuicaoMedicamento
    extra = 1

class DistribuicaoAdmin(admin.ModelAdmin):
    inlines = [DistribuicaoMedicamentoInline]
    list_display = ('estabelecimento_origem', 'estabelecimento_destino', 'data_atendimento')

admin.site.register(Operador, OperadorAdmin)
admin.site.register(Medicamento)
admin.site.register(EntradaEstoque)
admin.site.register(Paciente)
admin.site.register(Fornecedor)
admin.site.register(DetalhesMedicamento)
admin.site.register(Fabricante)
admin.site.register(Estabelecimento)
admin.site.register(PerfilOperador)
admin.site.register(Funcionalidade)
admin.site.register(Departamento)
admin.site.register(SaidaEstoque)
admin.site.register(Distribuicao, DistribuicaoAdmin)
admin.site.register(DistribuicaoMedicamento)







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
