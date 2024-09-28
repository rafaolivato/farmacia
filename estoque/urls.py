from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import saida_estoque, get_lotes, sucesso
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.base, name="base"),
    path("novo_paciente/", views.novo_paciente, name="novo_paciente"),
    path("lista_medicamentos/", views.lista_medicamentos, name="lista_medicamentos"),
    path("lista_pacientes/", views.lista_pacientes, name="lista_pacientes"),
    path('cadastro_fornecedor/', views.cadastro_fornecedor, name='cadastro_fornecedor'),
    path('cadastro_fabricante/', views.cadastro_fabricante, name='cadastro_fabricante'),
    path('cadastrar_medicamento/', views.cadastrar_medicamento, name ='cadastrar_medicamento'),
    path('sucesso/', views.sucesso, name='sucesso'), 
    path('entrada_estoque/', views.entrada_estoque, name='entrada_estoque'),
    path('cadastrar_localizacao/', views.cadastrar_localizacao, name ='cadastrar_localizacao'),
    path('lista_localizacoes/', views.lista_localizacoes, name='lista_localizacoes'),
    path('cadastrar_estabelecimento/', views.cadastrar_estabelecimento, name='cadastrar_estabelecimento'),
    path('lista_estabelecimentos/', views.lista_estabelecimentos, name='lista_estabelecimentos'),
    path('cadastrar_departamento/', views.cadastrar_departamento, name ='cadastrar_departamento'),
    path('lista_departamento/', views.lista_departamento, name='lista_departamento'),
    path('api/lotes_por_medicamento/', views.lotes_por_medicamento, name='lotes_por_medicamento'),
    path('cadastrar_operador/', views.cadastrar_operador, name='cadastrar_operador'),
    path('listar_operadores/', views.listar_operadores, name='listar_operadores'),
    path('cadastrar_medico/', views.cadastrar_medico, name='cadastrar_medico'),
    path('dispensacoes/', views.listar_dispensacoes, name='listar_dispensacoes'),
    path('dispensacoes/nova/', views.nova_dispensacao, name='nova_dispensacao'),
    path('dispensacoes/<int:id>/', views.detalhes_dispensacao, name='detalhes_dispensacao'),
    path('carregar_medicamentos_excel/', views.carregar_medicamentos_excel, name='carregar_medicamentos_excel'),
    path('cadastrar_medicamento/', views.cadastrar_medicamento, name='cadastrar_medicamento'),
    path('saida_estoque/', views.saida_estoque, name='saida_estoque'),
    path('get_lotes/', get_lotes, name='get_lotes'), 
    path('sucesso/',sucesso, name='sucesso'),
    path('accounts/', include('django.contrib.auth.urls')),  
    path('logout/', LogoutView.as_view(next_page='base'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='estoque/login.html', redirect_authenticated_user=True, next_page='base'), name='login'),
   
]
  
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



