# arvyo_core/urls.py

from django.contrib import admin
from django.urls import path, include
# >>> A linha que importava LoginView foi removida daqui! <<<

urlpatterns = [
    path('admin/', admin.site.urls),
    # Sua rota principal da API deve estar aqui:
    path('api/', include('financeiro_api.urls')), 
]