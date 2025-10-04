# financeiro_api/serializers.py

from rest_framework import serializers
from .models import Conta, Cartao, Lancamento, Floresta, Hábito, CumprimentoHábito

# --- Serializers para o CRUD e Dashboard ---

class ContaSerializer(serializers.ModelSerializer):
    """Serializer para Contas de saldo."""
    class Meta:
        model = Conta
        # Campos minimalistas para o MVP
        fields = ['id', 'nome', 'saldo_atual'] 
        read_only_fields = ['saldo_atual'] # Saldo_atual é calculado, não setado pelo usuário

class CartaoSerializer(serializers.ModelSerializer):
    """Serializer para Cartões de Crédito."""
    class Meta:
        model = Cartao
        # Foco no passivo (fatura_pendente)
        fields = ['id', 'nome', 'limite', 'fatura_pendente', 'dia_vencimento', 'dia_fechamento']
        read_only_fields = ['fatura_pendente'] # Fatura_pendente é calculada, não setada pelo usuário

class LancamentoSerializer(serializers.ModelSerializer):
    """Serializer principal para o Lançamento Rápido."""
    class Meta:
        model = Lancamento
        # Campos essenciais para a experiência de 2 cliques
        fields = [
            'id', 
            'tipo', 
            'valor', 
            'data', 
            'categoria', # A categoria 50/30/20 é essencial
            'tags',      # Tags opcionais para detalhe
            'descricao', 
            'conta', 
            'cartao',
            'conta_destino', # Apenas para transferências
        ] 
        # Garante que o usuário não precisa ver as chaves estrangeiras como IDs em todas as situações
        # depth = 1 # Opcional: para mostrar detalhes dos objetos relacionados (Conta/Cartão)

# --- Serializer para a Floresta ---

class FlorestaSerializer(serializers.ModelSerializer):
    """Serializer para exibir o progresso da gamificação."""
    class Meta:
        model = Floresta
        fields = ['pontos_acumulados', 'arvores_virtuais']
        read_only_fields = ['pontos_acumulados', 'arvores_virtuais'] # Valores só podem ser alterados via lógica do sistema

# --- Serializers de Gamificação ---

class HábitoSerializer(serializers.ModelSerializer):
    """Serializer para CRUD de Hábitos."""
    class Meta:
        model = Hábito
        fields = ['id', 'nome', 'descricao', 'pontos', 'ativo']
        read_only_fields = ['pontos'] # Simplificando: pontos fixos por enquanto

class CumprimentoHábitoSerializer(serializers.ModelSerializer):
    """Serializer para registrar o cumprimento de um Hábito."""
    hábito_nome = serializers.ReadOnlyField(source='hábito.nome')

    class Meta:
        model = CumprimentoHábito
        fields = ['id', 'hábito', 'hábito_nome', 'data', 'pontos_obtidos']
        read_only_fields = ['data', 'pontos_obtidos', 'hábito_nome']
