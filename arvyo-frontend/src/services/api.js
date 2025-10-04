// src/services/api.js (CÓDIGO SIMPLIFICADO E FINAL)

import axios from 'axios';
// Removidos: import Cookies, getCookie, e o bloco api.interceptors.request.use

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    // CRUCIAL: Diz ao navegador para incluir cookies de autenticação (sessão)
    withCredentials: true, 
    
    // CONFIGURAÇÕES NATIVAS DO AXIOS PARA CSRF (MAIS ESTÁVEL)
    // O Axios usará estas configurações para ler o 'csrftoken' do cookie 
    // e enviá-lo automaticamente no header 'X-CSRFToken' em POSTs.
    xsrfCookieName: 'csrftoken',       
    xsrfHeaderName: 'X-CSRFToken',      
});

// --- FUNÇÕES DE DADOS ---

export const fetchDashboardData = async () => {
    // Essa requisição agora deve retornar 401 (Não Autorizado) quando deslogado, e não 403 (Segurança)
    const response = await api.get('/dashboard/');
    return response.data;
};


// --- FUNÇÕES DE AUTENTICAÇÃO ---

export const login = async (username, password) => {
    // O Axios enviará o X-CSRFToken automaticamente agora graças à configuração acima
    const response = await api.post('/auth/login/', { username, password });
    return response.data; 
};

export const logout = async () => {
    await api.post('/auth/logout/');
};