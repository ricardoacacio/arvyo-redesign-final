// src/services/api.js

import axios from 'axios';

// 1. Cria a instância Axios
const api = axios.create({
    // Deve apontar para o Backend Django
    baseURL: 'http://127.0.0.1:8000/api',
    
    // CRUCIAL: Diz ao navegador para incluir cookies de autenticação (sessão e CSRF)
    withCredentials: true, 
    
    // CONFIGURAÇÕES NATIVAS DO AXIOS PARA CSRF (MAIS ESTÁVEL)
    xsrfCookieName: 'csrftoken',       
    xsrfHeaderName: 'X-CSRFToken',      
});

// --- FUNÇÕES DE DADOS ---

export const fetchDashboardData = async () => {
    // O Axios enviará o cookie de sessão para o endpoint protegido.
    const response = await api.get('/dashboard/');
    return response.data;
};


// --- FUNÇÕES DE AUTENTICAÇÃO ---

export const login = async (username, password) => {
    // POST: O Axios anexa o X-CSRFToken automaticamente.
    const response = await api.post('/auth/login/', { username, password });
    return response.data; 
};

// CRÍTICO: Função de Registro (Finalmente adicionada!)
export const register = async (username, email, password) => {
    // POST para o endpoint que criamos no Django.
    const response = await api.post('/auth/register/', { username, email, password });
    return response.data;
};

export const logout = async () => {
    // POST: O Axios anexa o X-CSRFToken automaticamente.
    await api.post('/auth/logout/');
};

// Exporta a instância para uso em interceptors, se necessário (opcional)
export default api;