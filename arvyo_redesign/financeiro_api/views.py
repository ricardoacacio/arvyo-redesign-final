# financeiro_api/views.py
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from .models import Conta, Cartao, Lancamento, Floresta, Hábito, CumprimentoHábito
from .serializers import ContaSerializer, CartaoSerializer, LancamentoSerializer, FlorestaSerializer, HábitoSerializer, CumprimentoHábitoSerializer
from .utils import atualizar_saldos_apos_lancamento
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny 
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.decorators import api_view, permission_classes # CRUCIAL para register_user
from .utils import calcula_saldo_real, calcula_progresso_503020, calcula_voce_pode_gastar_hoje, plantar_arvore_e_consumir_recursos
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.models import User # NOVO: Para o registro
from django.contrib.auth import authenticate, login as django_login, logout as logout_django
# Note: Removidas as imports: csrf_exempt e method_decorator

# --- ViewSets de Gestão (Contas, Cartões) ---

class ContaViewSet(viewsets.ModelViewSet):
    """API para CRUD de Contas. Filtra apenas as contas do usuário logado."""
    serializer_class = ContaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conta.objects.filter(usuario=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class CartaoViewSet(viewsets.ModelViewSet):
    """API para CRUD de Cartões de Crédito."""
    serializer_class = CartaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cartao.objects.filter(usuario=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

# --- ViewSet Central (Lançamentos) ---

class LancamentoViewSet(viewsets.ModelViewSet):
    """
    API para CRUD de Lançamentos. 
    Este ViewSet precisa da lógica CRÍTICA de atualização de saldo/fatura.
    """
    serializer_class = LancamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lancamento.objects.filter(usuario=self.request.user).order_by('-data')
        
    def perform_create(self, serializer):
        instance = serializer.save(usuario=self.request.user)
        try:
            atualizar_saldos_apos_lancamento(instance)
        except ValueError as e:
            instance.delete()
            # Certifique-se de importar serializers do rest_framework se usar esta linha:
            # raise serializers.ValidationError({"detalhe": str(e)})
            raise PermissionDenied({"detalhe": str(e)}) # Usamos PermissionDenied como fallback

# --- ViewSet da Gamificação (Floresta) ---

class FlorestaViewSet(viewsets.ReadOnlyModelViewSet):
    """API para visualizar o progresso da Floresta (Read-only, sem criação ou edição via API)"""
    serializer_class = FlorestaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        floresta, created = Floresta.objects.get_or_create(usuario=self.request.user)
        return Floresta.objects.filter(usuario=self.request.user)
    

class DashboardView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Usuário não autenticado.")
        
        # O Django deve ser configurado para calcular esses dados
        data = {
            "usuario_nome": request.user.username, # Adicione o nome do usuário aqui
            "saldo_real_consolidado": "12.500,00",
            "voce_pode_gastar_hoje": "2.100,00",
            "progresso_503020": {
                "renda_mensal": "5.000,00",
                "gastos_essencial": "2.500,00"
            }
        }
        return JsonResponse(data)
    
# NOTE: LoginView removida para evitar conflito de CSRF
    
class HábitoViewSet(viewsets.ModelViewSet):
    """API para CRUD de Hábitos."""
    serializer_class = HábitoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Hábito.objects.filter(usuario=self.request.user, ativo=True)
        
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class CumprimentoHábitoViewSet(viewsets.ModelViewSet):
    """API para registrar o cumprimento de um Hábito."""
    serializer_class = CumprimentoHábitoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CumprimentoHábito.objects.filter(hábito__usuario=self.request.user).order_by('-data')
        
    def perform_create(self, serializer):
        cumprimento = serializer.save()
        floresta = cumprimento.hábito.usuario.floresta
        floresta.pontos_acumulados += cumprimento.pontos_obtidos
        floresta.save()

class PlantarArvoreView(APIView):
    """Endpoint para plantar uma árvore virtual, consumindo Pontos ou Economia."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        tipo = request.data.get('tipo', None)
        user = request.user
        
        if not tipo:
            return Response({"detalhe": "O campo 'tipo' (PONTOS ou ECONOMIA) é obrigatório."}, status=400)
        
        sucesso, mensagem = plantar_arvore_e_consumir_recursos(user, tipo.upper())
        
        if sucesso:
            floresta = Floresta.objects.get(usuario=user)
            data = FlorestaSerializer(floresta).data
            data['mensagem'] = mensagem
            return Response(data, status=200)
        else:
            return Response({"detalhe": mensagem}, status=400)
        
# NOVO: Endpoint para Registro de Usuário (FINALIZADO)
@api_view(['POST'])
@permission_classes([AllowAny]) 
def register_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response(
            {"detalhe": "Todos os campos (username, email, password) são obrigatórios."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {"username": ["Este nome de usuário já está em uso."]},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"email": ["Este email já está em uso."]},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return Response(
            {"detalhe": "Usuário criado com sucesso!"},
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response(
            {"detalhe": f"Erro interno ao criar usuário: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
# NOVO: Endpoint para Login (FINAL)
@api_view(['POST'])
@permission_classes([AllowAny]) # Permite acesso para realizar o login
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        # A função django_login CRIA o cookie de sessão.
        django_login(request, user) 
        return Response({"message": "Login realizado com sucesso."}, status=status.HTTP_200_OK)
    else:
        # Retorna 400 Bad Request para credenciais inválidas.
        return Response({"detalhe": "Credenciais inválidas."}, status=status.HTTP_400_BAD_REQUEST)

# NOVO: Endpoint para Logout
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Só permite se o usuário estiver logado
def user_logout(request):
    # A função logout do Django remove o cookie de sessão.
    logout_django(request) 
    return Response({"message": "Logout realizado com sucesso."}, status=status.HTTP_200_OK)