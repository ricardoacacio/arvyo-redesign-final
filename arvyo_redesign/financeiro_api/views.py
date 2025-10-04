# financeiro_api/views.py
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from .models import Conta, Cartao, Lancamento, Floresta, Hábito, CumprimentoHábito
from .serializers import ContaSerializer, CartaoSerializer, LancamentoSerializer, FlorestaSerializer, HábitoSerializer, CumprimentoHábitoSerializer
from .utils import atualizar_saldos_apos_lancamento
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from .utils import calcula_saldo_real, calcula_progresso_503020, calcula_voce_pode_gastar_hoje, plantar_arvore_e_consumir_recursos
from django.contrib.auth import authenticate, login as django_login
from django.views.decorators.csrf import csrf_exempt 
from django.utils.decorators import method_decorator

# --- ViewSets de Gestão (Contas, Cartões) ---

class ContaViewSet(viewsets.ModelViewSet):
    """API para CRUD de Contas. Filtra apenas as contas do usuário logado."""
    serializer_class = ContaSerializer
    permission_classes = [permissions.IsAuthenticated] # Acesso apenas para usuários autenticados

    def get_queryset(self):
        # Garante que um usuário só possa ver/modificar suas próprias contas
        return Conta.objects.filter(usuario=self.request.user)
        
    def perform_create(self, serializer):
        # Associa a conta ao usuário logado automaticamente ao criar
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
        # Retorna lançamentos ordenados por data (mais recentes primeiro)
        return Lancamento.objects.filter(usuario=self.request.user).order_by('-data')
        
    def perform_create(self, serializer):
        # 1. Salva o lançamento, associando-o ao usuário.
        instance = serializer.save(usuario=self.request.user)

        # 2. Lógica Crítica de Atualização de Saldo (Passo 1.6)
        # Chamamos a função atômica após o lançamento ser salvo no DB
        try:
            atualizar_saldos_apos_lancamento(instance)
        except ValueError as e:
            # Se houver erro na lógica (ex: transferência inválida), removemos o lançamento
            # para manter a integridade (a transação.atomic já reverte, mas é bom garantir).
            instance.delete()
            # Poderíamos retornar um erro específico do DRF aqui
            raise serializers.ValidationError({"detalhe": str(e)})

        # Se tudo der certo, o lançamento e os saldos estão atualizados!

# --- ViewSet da Gamificação (Floresta) ---

class FlorestaViewSet(viewsets.ReadOnlyModelViewSet):
    """API para visualizar o progresso da Floresta (Read-only, sem criação ou edição via API)"""
    serializer_class = FlorestaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Certifica-se de que a Floresta existe para o usuário (ou cria se for a primeira vez)
        floresta, created = Floresta.objects.get_or_create(usuario=self.request.user)
        return Floresta.objects.filter(usuario=self.request.user)
    

class DashboardView(APIView):
    # Usamos o SessionAuthentication para gerenciar o cookie de sessão.
    authentication_classes = [SessionAuthentication]
    # Usamos IsAuthenticated para garantir que apenas usuários logados vejam os dados.
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        
        # O DRF deve cuidar de verificar o login automaticamente. 
        # No entanto, em um setup de cookies entre portas (que é o que temos), 
        # o DRF pode retornar 403 em vez de 401. 
        
        # Se request.user não estiver autenticado (ou seja, não há sessão), 
        # levantamos explicitamente uma exceção de não autenticação.
        if not request.user.is_authenticated:
            # Isso força o DRF a retornar o status 401 (Unauthorized), 
            # que é o que o Front-end espera para ir para a tela de Login.
            raise NotAuthenticated("Usuário não autenticado.")
        
        # --- Lógica que só roda se o usuário REALMENTE estiver logado (200 OK) ---
        
        data = {
            "saldo_real_consolidado": "12.500,00",
            "voce_pode_gastar_hoje": "2.100,00",
            "progresso_503020": {
                "renda_mensal": "5.000,00",
                "gastos_essencial": "2.500,00"
            }
        }
        return JsonResponse(data)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    DIAGNÓSTICO: Endpoint de Login TEMPORÁRIO que ignora o CSRF para fins de teste.
    """
    # Deixamos em branco para permitir a requisição POST
    permission_classes = [] 
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # O Login do Django cria o cookie de sessão.
            django_login(request, user) 
            return JsonResponse({"message": "Login realizado com sucesso."})
        else:
            # Retorna 400 se as credenciais estiverem erradas
            return JsonResponse({"error": "Credenciais inválidas."}, status=400)

    
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
        # Retorna apenas os cumprimentos do usuário logado
        return CumprimentoHábito.objects.filter(hábito__usuario=self.request.user).order_by('-data')
        
    def perform_create(self, serializer):
        # 1. Salva o Cumprimento
        cumprimento = serializer.save()
        
        # 2. Lógica Crítica: Atualiza os Pontos na Floresta (Passo 3.3)
        # Vamos assumir que a Floresta do usuário existe (get_or_create na FlorestaViewSet)
        floresta = cumprimento.hábito.usuario.floresta
        floresta.pontos_acumulados += cumprimento.pontos_obtidos
        floresta.save()

class PlantarArvoreView(APIView):
    """Endpoint para plantar uma árvore virtual, consumindo Pontos ou Economia."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        tipo = request.data.get('tipo', None) # Espera 'PONTOS' ou 'ECONOMIA'
        user = request.user
        
        if not tipo:
            return Response({"detalhe": "O campo 'tipo' (PONTOS ou ECONOMIA) é obrigatório."}, status=400)
        
        sucesso, mensagem = plantar_arvore_e_consumir_recursos(user, tipo.upper())
        
        if sucesso:
            # Retorna o status atualizado da floresta
            floresta = Floresta.objects.get(usuario=user)
            data = FlorestaSerializer(floresta).data
            data['mensagem'] = mensagem
            return Response(data, status=200)
        else:
            # Retorna erro 400 (Bad Request) com a mensagem de falha
            return Response({"detalhe": mensagem}, status=400)