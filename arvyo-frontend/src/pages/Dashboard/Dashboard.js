// src/components/Dashboard.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext'; 
import { fetchDashboardData } from '../../services/api'; 

const DashboardPage = () => {
    // 1. Pega os estados de autenticação
    const { isLoggedIn, loginUser } = useAuth(); 
    
    // 2. Cria um estado para armazenar os dados reais que virão do Django
    const [dashboardData, setDashboardData] = useState(null);
    const [isLoadingData, setIsLoadingData] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Se o usuário estiver logado, busca os dados
        if (isLoggedIn) {
            const loadData = async () => {
                try {
                    const data = await fetchDashboardData();
                    setDashboardData(data);
                    setIsLoadingData(false);
                } catch (err) {
                    // Se falhar (ex: token expirou, 401/403), desloga ou mostra erro
                    setError("Falha ao carregar dados do Dashboard. Tente logar novamente.");
                    setIsLoadingData(false);
                }
            };
            loadData();
        } else {
            // Se não estiver logado (e o AuthContext já finalizou o carregamento inicial),
            // podemos redirecionar ou mostrar a tela de Login
            setIsLoadingData(false);
        }
    }, [isLoggedIn]); // Roda sempre que o estado de login mudar

    // --- Lógica de Exibição ---

    if (isLoadingData) {
        // Mostra um loading ENQUANTO busca os dados da API
        return <div>Carregando dados do Dashboard...</div>;
    }

    if (!isLoggedIn) {
        // Se não está logado, mostra a tela de login (você deve implementar o redirecionamento aqui)
        return <div>Você precisa estar logado para ver o Dashboard. (Implementar Tela de Login/Redirecionamento)</div>;
    }

    if (error) {
         // Se deu erro na busca dos dados
        return <div>Erro: {error}</div>;
    }
    
    // 3. Exibe os dados reais do Django
    const saldo = dashboardData?.saldo_real_consolidado || 0;
    const saldoFormatado = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(saldo);


    return (
        <div style={{ padding: '20px' }}>
            <h2>Bem-vindo, {dashboardData?.usuario_nome || 'Usuário'}!</h2>
            <div style={{ padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
                <h3>Saldo Real Consolidado</h3>
                <p style={{ fontSize: '2em', fontWeight: 'bold', color: 'green' }}>
                    {saldoFormatado}
                </p>
                <p>O valor é a soma de todas as suas contas ativas.</p>
            </div>
            {/* Você continuará a implementar a tela aqui, seguindo seu modelo de design */}
        </div>
    );
};

export default DashboardPage;