// src/context/AuthContext.js

import React, { createContext, useState, useContext, useEffect } from 'react';
import { login, logout, fetchDashboardData } from '../services/api';

// 1. Cria o Contexto
export const AuthContext = createContext();

// 2. Cria o Provedor do Contexto
export const AuthProvider = ({ children }) => {
  // Estado principal que diz se o usuário está autenticado
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  // Efeito para verificar o status de login ao carregar a aplicação
  useEffect(() => {
    // Tentamos acessar um recurso protegido (Dashboard)
    // Se funcionar, estamos logados. Se der 401/403, não estamos.
    const checkLoginStatus = async () => {
      try {
        await fetchDashboardData(); 
        setIsLoggedIn(true); // Se conseguiu os dados, está logado
      } catch (error) {
        setIsLoggedIn(false); // Se deu erro de permissão (401/403), não está logado
      } finally {
        setLoading(false);
      }
    };

    checkLoginStatus();
  }, []);

  // Função de Login
  const loginUser = async (username, password) => {
    try {
      // Chama a função login da API
      await login(username, password); 
      setIsLoggedIn(true);
      // O retorno true/false é útil para redirecionar o usuário
      return true; 
    } catch (error) {
      console.error("Login falhou:", error);
      // O erro pode ser de credenciais inválidas (400) ou outro problema.
      throw error; 
    }
  };

  // Função de Logout
  const logoutUser = async () => {
    try {
      await logout();
      setIsLoggedIn(false);
    } catch (error) {
      console.error("Logout falhou:", error);
    }
  };

  if (loading) {
    return <div>Carregando estado inicial...</div>;
  }

  // O valor que será compartilhado com toda a aplicação
  const contextValue = {
    isLoggedIn,
    loginUser,
    logoutUser,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook customizado para usar o AuthContext em qualquer componente
export const useAuth = () => {
  return useContext(AuthContext);
};