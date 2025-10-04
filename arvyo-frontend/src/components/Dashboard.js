// src/components/Dashboard.js (CÓDIGO CORRIGIDO V.2)

import React, { useState, useEffect } from 'react';
import { fetchDashboardData } from '../services/api'; 
import { useAuth } from '../context/AuthContext'; 
import LoginScreen from './LoginScreen'; 

function Dashboard() {
  // --- TODOS OS HOOKS PRECISAM SER CHAMADOS NO TOPO ---
  const { isLoggedIn, logoutUser } = useAuth(); // ESTE É O PRIMEIRO HOOK!
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // A LÓGICA DO DASHBOARD SÓ É EXECUTADA SE ESTIVER LOGADO
  useEffect(() => {
    if (isLoggedIn) {
      const loadData = async () => {
        try {
          const dashboardData = await fetchDashboardData();
          setData(dashboardData);
          setLoading(false);
        } catch (err) {
          setError("Erro ao buscar dados mesmo logado. Sessão expirou?");
          console.error(err);
          setLoading(false);
        }
      };
      
      setLoading(true); 
      loadData();
    }
  }, [isLoggedIn]);

  // --- RETORNO CONDICIONAL ---

  // 1. Se não estiver logado, mostre a tela de Login
  if (!isLoggedIn) {
    return <LoginScreen />;
  }

  // 2. Se estiver logado, mas ainda carregando...
  if (loading) return <p>Carregando Dashboard...</p>;
  
  // 3. Se deu erro ao carregar os dados
  if (error) return <p style={{ color: 'red', fontWeight: 'bold' }}>{error}</p>;

  // --- 4. TELA DE SUCESSO DO DASHBOARD ---
  return (
    <div style={{ padding: '20px', border: '1px solid green', margin: '20px' }}>
      <h2>DADOS FINANCEIROS ARVYO</h2>
      <button onClick={logoutUser} style={{ float: 'right', padding: '10px', background: 'red', color: 'white', border: 'none' }}>
        Sair (Logout)
      </button>
      
      <p>
        **Saldo Real Consolidado:** <strong style={{color: 'green'}}>R$ {data.saldo_real_consolidado}</strong>
      </p>
      <p>
        **Você Pode Gastar Hoje:** <strong style={{color: 'blue'}}>R$ {data.voce_pode_gastar_hoje}</strong>
      </p>
      <hr />
      <h3>Progresso 50/30/20</h3>
      <p>Renda Mensal: R$ {data.progresso_503020.renda_mensal}</p>
      <p>Gastos Essenciais: R$ {data.progresso_503020.gastos_essencial}</p>
    </div>
  );
}

export default Dashboard;