# arvyo_core/urls.py

from django.contrib import admin
from django.urls import path, include
from financeiro_api.views import LoginView # NOVIDADE: Importe a view que você criou



urlpatterns = [
    # Inclui as rotas de autenticação do Django Admin
    path('admin/', admin.site.urls), 
    
    # 1. NOVIDADE: Mapeia nossa view de Login temporária, no endpoint que o React espera
    path('api/auth/login/', LoginView.as_view(), name='api-login'), 
    # Inclui todas as rotas da nossa API, prefixadas com 'api/'
    path('api/', include('financeiro_api.urls')),
    
]