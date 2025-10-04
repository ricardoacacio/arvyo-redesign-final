# financeiro_api/utils.py

from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce 
from .models import Conta, Cartao, Lancamento, Floresta
from decimal import Decimal # Garanta que este também está importado

# IMPORT NECESSÁRIO A SER ADICIONADO:
from datetime import date 
# Fim do bloco de imports

# Definimos as regras de negócio para atualização de saldo aqui.

@transaction.atomic
def atualizar_saldos_apos_lancamento(lancamento_instance: Lancamento):
    """
    Atualiza atomicamente os saldos da Conta ou Cartão após um Lancamento.
    
    Atenção: A função pressupõe que o valor do Lancamento está sempre positivo no DB.
    O impacto (+ ou -) é definido pelo 'tipo' do lançamento.
    """
    
    valor = lancamento_instance.valor
    tipo = lancamento_instance.tipo
    conta_origem = lancamento_instance.conta
    cartao_usado = lancamento_instance.cartao
    
    if tipo == 'RECEITA':
        # 1. Entrada de dinheiro sempre impacta a CONTA
        if conta_origem:
            conta_origem.saldo_atual += valor
            conta_origem.save()
            
    elif tipo == 'DESPESA':
        # 2. Saída de dinheiro pode vir de CONTA ou CARTÃO
        if conta_origem:
            # Despesa paga com dinheiro/débito
            conta_origem.saldo_atual -= valor
            conta_origem.save()
        
        elif cartao_usado:
            # Despesa no cartão de crédito: aumenta a fatura pendente (passivo)
            cartao_usado.fatura_pendente += valor
            cartao_usado.save()

    elif tipo == 'TRANSFERENCIA':
        conta_destino = lancamento_instance.conta_destino
        
        # 3. Transferência: Debita de Origem e Credita em Destino (não impacta Receita/Despesa)
        if conta_origem and conta_destino:
            
            # Debita da conta de origem
            conta_origem.saldo_atual -= valor
            conta_origem.save()
            
            # Credita na conta de destino
            conta_destino.saldo_atual += valor
            conta_destino.save()
        else:
            # Se for transferência, ambas as contas são obrigatórias
            # Caso contrário, lança um erro para reverter a transação.
            raise ValueError("Transferência requer Conta de origem e Conta de destino.")
            
    # Se nenhuma das condições acima for atendida (ex: despesa sem conta/cartão), 
    # o lançamento existe, mas não altera o saldo, o que pode ser uma regra de negócio válida (ex: gasto não contabilizado).
    
    # Esta função está protegida por @transaction.atomic. Se ocorrer qualquer erro 
    # (ex: valor negativo ou Conta inexistente), todas as alterações de DB são desfeitas.

def calcula_saldo_real(user):
    """
    Calcula o Saldo Real Consolidado do usuário:
    Soma(saldos em conta) - Soma(faturas pendentes do cartão)
    """
    
    # 1. Total de saldos em contas (Ativos). Se não houver contas, retorna 0.
    contas_sum = Conta.objects.filter(usuario=user).aggregate(total=Sum('saldo_atual'))['total'] or 0
    
    # 2. Total de faturas pendentes (Passivos). Se não houver cartões, retorna 0.
    cartoes_sum = Cartao.objects.filter(usuario=user).aggregate(total=Sum('fatura_pendente'))['total'] or 0
    
    saldo_real = contas_sum - cartoes_sum
    
    # Retorna um objeto Decimal (essencial para evitar erros de precisão com dinheiro)
    return saldo_real


def calcula_progresso_503020(user, mes=None, ano=None):
    """
    Calcula o progresso de gastos em relação à regra 50/30/20 para o mês/ano.
    Retorna os totais gastos por categoria (Essencial, Estilo de Vida, Futuro).
    """
    if mes is None or ano is None:
        hoje = date.today()
        mes = hoje.month
        ano = hoje.year

    # 1. Filtra todos os Lançamentos do mês atual
    lancamentos_do_mes = Lancamento.objects.filter(
        usuario=user,
        data__month=mes,
        data__year=ano
    ).exclude(tipo='TRANSFERENCIA') # Transferências não são Receita/Despesa 

    # 2. Calcula a Renda Mensal Total (Soma de todas as RECEITAS)
    renda_mensal = lancamentos_do_mes.filter(tipo='RECEITA').aggregate(
        total=Coalesce(Sum('valor'), Decimal('0.00'))
    )['total']
    
    # Se não houver receita registrada, não podemos orçar.
    if renda_mensal == 0:
        return {
            'renda_mensal': 0,
            'gastos_essencial': 0,
            'gastos_estilo': 0,
            'gastos_futuro': 0,
            'limite_essencial': 0,
            'limite_estilo': 0,
            'limite_futuro': 0,
        }

    # 3. Define os Limites (Orçamento) baseado na Renda
    # Conversão para Decimal é crucial para garantir a precisão
    limite_essencial = renda_mensal * Decimal('0.50')
    limite_estilo = renda_mensal * Decimal('0.30')
    limite_futuro = renda_mensal * Decimal('0.20')

    # 4. Soma os Gastos (DESPESAS) por Categoria
    gastos_por_categoria = lancamentos_do_mes.filter(tipo='DESPESA').values('categoria').annotate(
        gasto_total=Coalesce(Sum('valor'), Decimal('0.00'))
    )

    # Inicializa os gastos
    gastos = {
        'ESSENCIAL': Decimal('0.00'),
        'ESTILO_DE_VIDA': Decimal('0.00'),
        'FUTURO': Decimal('0.00')
    }
    for item in gastos_por_categoria:
        gastos[item['categoria']] = item['gasto_total']
        
    return {
        'renda_mensal': renda_mensal,
        'gastos_essencial': gastos['ESSENCIAL'],
        'gastos_estilo': gastos['ESTILO_DE_VIDA'],
        'gastos_futuro': gastos['FUTURO'],
        'limite_essencial': limite_essencial,
        'limite_estilo': limite_estilo,
        'limite_futuro': limite_futuro,
    }


def calcula_voce_pode_gastar_hoje(user):
    """
    Calcula a métrica principal: Saldo Real disponível para gastos não essenciais
    no Estilo de Vida e Essencial, assumindo o 50/30/20.
    """
    
    # 1. Saldo Real Consolidado
    saldo_real = calcula_saldo_real(user)
    
    # 2. Progresso 50/30/20 (para pegar limites e gastos)
    progresso = calcula_progresso_503020(user)
    
    # 3. Dinheiro alocado para Despesas Essenciais e Estilo de Vida
    limite_gasto = progresso['limite_essencial'] + progresso['limite_estilo']
    
    # 4. O quanto já foi gasto do Essencial/Estilo de Vida (o que PRECISA ser pago)
    gastos_gasto = progresso['gastos_essencial'] + progresso['gastos_estilo']
    
    # O valor que AINDA pode ser gasto nas categorias de consumo (50%+30%)
    saldo_orcamento_consumo = limite_gasto - gastos_gasto
    
    # A métrica final do Arvyo:
    # Quanto você tem no bolso (Saldo Real) menos o que já foi gasto em consumo,
    # comparado ao que o orçamento de consumo te permite.
    
    # A maneira mais simples e segura: Qual é o seu Saldo Real, 
    # menos a alocação de Futuro (20%)?
    
    # Se o usuário está abaixo do limite Futuro (20%), 
    # o restante do Saldo Real é teoricamente disponível.
    
    # Para ser mais conservador e minimalista (o conceito do Arvyo):
    # 'Você pode gastar hoje' = Saldo Real - (Limite Futuro 20%) - (Gastos Essenciais/Estilo já feitos)
    
    # Vamos usar uma métrica simples: Saldo de Consumo Disponível.
    # Isto é o Saldo Real menos tudo que DEVERIA ir para o Futuro.
    
    valor_futuro_a_ser_alocado = progresso['limite_futuro']
    
    voce_pode_gastar = saldo_real - valor_futuro_a_ser_alocado
    
    # Não pode ser negativo, se for negativo, você está devendo!
    return max(Decimal('0.00'), voce_pode_gastar)


PONTOS_POR_ARVORE = 500
VALOR_ECONOMIA_POR_ARVORE = Decimal('500.00')

def calcula_economia_real(user):
    """
    Calcula o excedente no orçamento de consumo (50% Essencial + 30% Estilo de Vida).
    Economia = Limite de Consumo - Gastos de Consumo.
    """
    progresso = calcula_progresso_503020(user)

    limite_consumo = progresso['limite_essencial'] + progresso['limite_estilo']
    gastos_consumo = progresso['gastos_essencial'] + progresso['gastos_estilo']

    economia = limite_consumo - gastos_consumo
    
    # Retorna o excedente (pode ser negativo se o usuário estourou o limite)
    return economia


@transaction.atomic
def plantar_arvore_e_consumir_recursos(user, tipo_conversao):
    """
    Tenta converter pontos de hábito ou economia real em 1 Árvore Virtual.
    Consome os recursos equivalentes.
    """
    floresta = Floresta.objects.get(usuario=user)
    
    if tipo_conversao == 'PONTOS':
        if floresta.pontos_acumulados >= PONTOS_POR_ARVORE:
            # Consome pontos e planta a árvore
            floresta.pontos_acumulados -= PONTOS_POR_ARVORE
            floresta.arvores_virtuais += 1
            floresta.save()
            return True, f"Sucesso! 1 Árvore plantada consumindo {PONTOS_POR_ARVORE} pontos de hábito."
        else:
            pontos_faltantes = PONTOS_POR_ARVORE - floresta.pontos_acumulados
            return False, f"Pontos insuficientes. Faltam {pontos_faltantes} pontos para plantar via hábito."
            
    elif tipo_conversao == 'ECONOMIA':
        economia_disponivel = calcula_economia_real(user)
        
        if economia_disponivel >= VALOR_ECONOMIA_POR_ARVORE:
            # Planta a árvore (a economia é um cálculo, não precisa ser "consumida" no DB)
            # A economia é um valor *excedente* de consumo, não um saldo em conta.
            floresta.arvores_virtuais += 1
            floresta.save()
            
            # NOTA: Não alteramos nenhum campo financeiro (saldo/lançamento) aqui.
            # A ação é apenas um símbolo de recompensa pela boa gestão.
            return True, f"Sucesso! 1 Árvore plantada graças a uma economia de R${VALOR_ECONOMIA_POR_ARVORE} no seu orçamento de consumo."
        else:
            economia_faltante = VALOR_ECONOMIA_POR_ARVORE - economia_disponivel
            # Usamos o max(0, ...) para evitar números positivos se a economia for negativa
            economia_faltante = max(Decimal('0.00'), economia_faltante)
            return False, f"Economia insuficiente. Você precisa de R${VALOR_ECONOMIA_POR_ARVORE} de excedente e tem R${economia_disponivel}."
            
    return False, "Tipo de conversão inválido."

def calcula_saldo_real_consolidado(user):
    """
    Calcula a soma dos saldos de todas as contas do usuário.
    Retorna o valor total (float).
    """
    # Importa o modelo Conta aqui para evitar problemas de dependência circular
    from .models import Conta 
    
    # Filtra as contas pelo usuário e soma o campo 'saldo_atual'
    saldo_total = Conta.objects.filter(usuario=user).aggregate(Sum('saldo_atual'))['saldo_atual__sum']
    
    # Se o usuário não tiver contas, a soma será None. Retornamos 0.0 nesse caso.
    return saldo_total if saldo_total is not None else 0.0