// src/context/AuthContext.js

import React, { createContext, useState, useContext, useEffect } from 'react';
// CRÍTICO: Adicione 'register' ao import abaixo!
import { login, logout, fetchDashboardData, register } from '../services/api'; 

// 1. Cria o Contexto
export const AuthContext = createContext();

// 2. Cria o Provedor do Contexto
export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        await fetchDashboardData(); 
        setIsLoggedIn(true);
      } catch (error) {
        setIsLoggedIn(false);
      } finally {
        setLoading(false);
      }
    };

    checkLoginStatus();
  }, []);

  // --- FUNÇÃO DE LOGIN (OK) ---
  const loginUser = async (username, password) => {
    try {
      await login(username, password); 
      setIsLoggedIn(true);
      return true; 
    } catch (error) {
      console.error("Login falhou:", error);
      throw error; 
    }
  };

  // --- FUNÇÃO DE CADASTRO (NOVA) ---
  const registerUser = async (username, email, password) => {
    try {
      // Chama a função 'register' do api.js (agora que ela existe lá)
      await register(username, email, password); 
      // Não faz login, apenas retorna sucesso
      return true; 
    } catch (error) {
      console.error("Cadastro falhou:", error.response?.data || error.message);
      // Retorna o erro exato do backend (ex: "email já em uso")
      throw error.response?.data || { detalhe: "Erro desconhecido ao cadastrar." };
    }
  };

  // --- FUNÇÃO DE LOGOUT (OK) ---
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
    registerUser, // CRÍTICO: Exportar a função de Cadastro
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