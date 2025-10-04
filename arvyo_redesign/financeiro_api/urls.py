# financeiro_api/urls.py

from rest_framework.routers import DefaultRouter
from .views import ContaViewSet, CartaoViewSet, LancamentoViewSet, FlorestaViewSet, DashboardView, HábitoViewSet, CumprimentoHábitoViewSet, PlantarArvoreView # Adicione DashboardView
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
]

urlpatterns += router.urls