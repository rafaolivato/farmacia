from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import saida_estoque,sucesso
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import criar_requisicao, listar_requisicoes, responder_requisicao
from .views import medicamentos_por_estabelecimento, confirmar_requisicao, receber_requisicoes, entrada_estoque, distribuir_medicamento


urlpatterns = [
    path("", views.base, name="base"),
    path('login/', auth_views.LoginView.as_view(template_name='estoque/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
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
    path('api/lotes_por_medicamento/<int:medicamento_id>/', views.lotes_por_medicamento, name='lotes_por_medicamento'),
    path('cadastrar_medico/', views.cadastrar_medico, name='cadastrar_medico'),
    path('dispensacoes/', views.listar_dispensacoes, name='listar_dispensacoes'),
    path('dispensacoes/nova/', views.nova_dispensacao, name='nova_dispensacao'),
    path('dispensacoes/<int:id>/', views.detalhes_dispensacao, name='detalhes_dispensacao'),
    path('carregar_medicamentos_excel/', views.carregar_medicamentos_excel, name='carregar_medicamentos_excel'),
    path('cadastrar_medicamento/', views.cadastrar_medicamento, name='cadastrar_medicamento'),
    path('sucesso/',sucesso, name='sucesso'),
    path('accounts/', include('django.contrib.auth.urls')),  
    path('saida_estoque/', views.saida_estoque, name='saida_estoque'),
    path('estoque/dispensacoes/<int:id>/', views.detalhes_dispensacao, name='detalhes_dispensacao'),
    path('distribuir_medicamento/', distribuir_medicamento, name='distribuir_medicamento'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('requisicoes/criar/', criar_requisicao, name='criar_requisicao'),
    path('requisicoes/', listar_requisicoes, name='listar_requisicoes'),
    path('requisicoes/<int:requisicao_id>/responder/', responder_requisicao, name='responder_requisicao'),
    path('api/medicamentos_por_estabelecimento/<int:estabelecimento_id>/', medicamentos_por_estabelecimento, name='medicamentos_por_estabelecimento'),
    path('requisicoes/confirmar/<int:pk>/', confirmar_requisicao, name='confirmar_requisicao'),
    path('requisicoes/receber/', receber_requisicoes, name='receber_requisicoes'),
   
]
  

 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




