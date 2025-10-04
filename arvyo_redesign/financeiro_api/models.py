# financeiro_api/models.py
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# --- Constantes do Sistema (as 3 categorias de alocação) ---
CATEGORIA_CHOICES = (
    ('ESSENCIAL', 'Essencial (Necessidades - 50%)'),
    ('ESTILO_DE_VIDA', 'Estilo de Vida (Desejos - 30%)'),
    ('FUTURO', 'Futuro (Poupança/Investimento - 20%)'),
)

TIPO_LANCAMENTO_CHOICES = (
    ('RECEITA', 'Receita'),
    ('DESPESA', 'Despesa'),
    ('TRANSFERENCIA', 'Transferência'), # Não impacta Receita/Despesa, só saldos
)

# --- CORE FINANCEIRO (Etapa 1) ---

class Conta(models.Model):
    """Contas de saldo (Corrente, Poupança, Dinheiro)"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contas')
    nome = models.CharField(max_length=100)
    # Saldo atual da conta. Decimal é essencial para dinheiro.
    saldo_atual = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    def __str__(self):
        return f"{self.nome} ({self.usuario.username})"

class Cartao(models.Model):
    """Cartões de Crédito (fatura é um passivo no saldo real)"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cartoes')
    nome = models.CharField(max_length=100)
    limite = models.DecimalField(max_digits=12, decimal_places=2)
    # Valor total de gastos na fatura atual - é um PASSIVO que entra no Saldo Real
    fatura_pendente = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    dia_vencimento = models.IntegerField()
    dia_fechamento = models.IntegerField()

    def __str__(self):
        return f"{self.nome} ({self.usuario.username})"

class Lancamento(models.Model):
    """Registro de todas as transações (Receitas, Despesas, Transferências)"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_LANCAMENTO_CHOICES)
    
    # Detalhe do lançamento
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField()
    
    # Categorização simples (as 3 fixas para o 50/30/20)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, null=True, blank=True)
    
    # Detalhe opcional (para o Kakebo e relatórios detalhados)
    descricao = models.TextField(blank=True, null=True)
    # Tags para o detalhe (ex: #Alimentação, #Transporte), mantendo a categoria principal limpa
    tags = models.CharField(max_length=255, blank=True, help_text="Tags opcionais (Ex: #alimentação, #viagem)")

    # Contas envolvidas
    conta = models.ForeignKey(Conta, on_delete=models.SET_NULL, null=True, blank=True, help_text="Conta de origem/destino do valor.")
    cartao = models.ForeignKey(Cartao, on_delete=models.SET_NULL, null=True, blank=True, help_text="Cartão utilizado na despesa.")
    
    # Usado APENAS em transferências (tipo='TRANSFERENCIA')
    conta_destino = models.ForeignKey(Conta, on_delete=models.SET_NULL, null=True, blank=True, related_name='transferencias_recebidas')

    def __str__(self):
        return f"[{self.data}] {self.tipo}: R${self.valor} ({self.get_categoria_display()})"

    # Regra de Negócio: Garante que o valor sempre seja positivo no DB.
    def save(self, *args, **kwargs):
        if self.valor < 0:
            self.valor = self.valor * -1
        super().save(*args, **kwargs)


# --- GAMIFICAÇÃO & PROPÓSITO (MVP Simbólico) ---

class Floresta(models.Model):
    """Armazena o progresso do usuário em relação à Floresta Virtual"""
    # OneToOne: cada usuário tem apenas uma Floresta
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    pontos_acumulados = models.IntegerField(default=0)
    arvores_virtuais = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Floresta de {self.usuario.username}: {self.arvores_virtuais} árvores"
    

# --- GAMIFICAÇÃO & PROPÓSITO (Expansão) ---

class Hábito(models.Model):
    """
    Representa um hábito financeiro que o usuário pode completar para ganhar pontos.
    (Ex: Revisar gastos, Registrar tudo no dia, Meditar sobre as metas).
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habitos')
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)
    pontos = models.IntegerField(default=10) # Pontuação por cumprimento
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Hábito: {self.nome} ({self.pontos} pts)"

class CumprimentoHábito(models.Model):
    """Registro de quando um hábito foi cumprido (Diário)."""
    hábito = models.ForeignKey(Hábito, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)
    pontos_obtidos = models.IntegerField()
    
    def save(self, *args, **kwargs):
        # Garante que os pontos são registrados no momento do cumprimento
        if not self.pontos_obtidos:
            self.pontos_obtidos = self.hábito.pontos
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.hábito.nome} cumprido em {self.data}"