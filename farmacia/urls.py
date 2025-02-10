
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from estoque import views as estoque_views  # Importe suas views
from estoque.views import lotes_por_medicamento,medicamentos_por_estabelecimento

urlpatterns = [
    path('admin/', admin.site.urls),
    path('estoque/', include('estoque.urls')),
    path('api/lotes_por_medicamento/<int:medicamento_id>/', lotes_por_medicamento, name='lotes_por_medicamento'),
    path('login/', auth_views.LoginView.as_view(template_name='estoque/login.html', redirect_authenticated_user=True), name='login'),  # URL de login
    path('', RedirectView.as_view(url='/estoque/', permanent=True)),  # Redireciona a URL raiz para /estoque/
    path('api/medicamentos_por_estabelecimento/<int:estabelecimento_id>/', medicamentos_por_estabelecimento, name='medicamentos_por_estabelecimento'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)








