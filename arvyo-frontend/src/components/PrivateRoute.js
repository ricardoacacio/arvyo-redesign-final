// src/components/PrivateRoute.js
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; 

export const PrivateRoute = ({ element: Element, ...rest }) => {
    // Usa a lógica de autenticação que você já tem
    const { isLoggedIn, loading } = useAuth(); 
    
    if (loading) {
        // Deve ser muito rápido, mas é bom para garantir UX
        return <div>Verificando autenticação...</div>;
    }

    // Se estiver logado, renderiza o componente, senão, redireciona para a página inicial
    return isLoggedIn ? <Element {...rest} /> : <Navigate to="/login" replace />;
};