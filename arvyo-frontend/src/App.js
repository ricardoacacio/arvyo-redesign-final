// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext'; // Usa seu AuthProvider

// --- Componentes Essenciais ---
import { PrivateRoute } from './components/PrivateRoute';

// --- PÁGINAS (Você criará estas pastas em src/pages/) ---
import HomePage from './pages/Home/Home';       // Rota: /
import LoginPage from './pages/Login/Login';     // Rota: /login
import RegisterPage from './pages/Register/Register'; // Rota: /cadastro
import DashboardPage from './pages/Dashboard/Dashboard'; // Rota: /dashboard


const App = () => {
    // Usamos o AuthProvider para envolver o roteador
    return (
        <AuthProvider> 
            <AppRouter />
        </AuthProvider>
    );
};

const AppRouter = () => {
    const { loading } = useAuth(); // Usa o estado de loading do seu AuthContext

    if (loading) {
        // Exibe um loading enquanto verifica o status da sessão inicial
        return <div>Carregando aplicação e verificando sessão...</div>;
    }
    
    return (
        <Router>
            <Routes>
                {/* 1. ROTAS PÚBLICAS (Todos têm acesso) */}
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/cadastro" element={<RegisterPage />} />
                
                {/* 2. ROTA PRIVADA (Apenas usuários logados) */}
                <Route 
                    path="/dashboard" 
                    element={<PrivateRoute element={DashboardPage} />} 
                />
                
                {/* Rota 404/Not Found, se desejar */}
            </Routes>
        </Router>
    );
}

export default App;