# financeiro_api/urls.py

from rest_framework.routers import DefaultRouter
from .views import ContaViewSet, CartaoViewSet, LancamentoViewSet, FlorestaViewSet, DashboardView, HábitoViewSet, CumprimentoHábitoViewSet, PlantarArvoreView, register_user, user_login, user_logout
from django.urls import path # Adicione este import
from rest_framework.routers import DefaultRouter


# O DefaultRouter do DRF cria automaticamente as rotas CRUD (list, detail, create, update, delete)
router = DefaultRouter()
router.register(r'contas', ContaViewSet, basename='conta')
router.register(r'cartoes', CartaoViewSet, basename='cartao')
router.register(r'lancamentos', LancamentoViewSet, basename='lancamento')
router.register(r'floresta', FlorestaViewSet, basename='floresta')
router.register(r'habitos', HábitoViewSet, basename='hábito')
router.register(r'cumprimentos', CumprimentoHábitoViewSet, basename='cumprimento')

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('plantar-arvore/', PlantarArvoreView.as_view(), name='plantar_arvore'),
    path('auth/register/', register_user, name='register'),
    path('auth/login/', user_login, name='login'),
    path('auth/logout/', user_logout, name='logout'),
]

urlpatterns += router.urls