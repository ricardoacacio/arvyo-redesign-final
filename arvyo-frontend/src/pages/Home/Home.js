// src/pages/Home/Home.js
import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
    return (
        <div style={{ padding: '50px', textAlign: 'center', backgroundColor: '#f0f4f8' }}>
            <h1>Bem-vindo(a) ao Arvyo - Seu Gestor Financeiro e de Hábitos</h1>
            <p style={{ fontSize: '1.2em', color: '#555' }}>
                Transforme suas finanças e plante uma floresta virtual com seus bons hábitos.
            </p>

            <div style={{ marginTop: '40px' }}>
                {/* Botão de Login */}
                <Link 
                    to="/login" 
                    style={{ 
                        padding: '12px 25px', 
                        marginRight: '20px',
                        backgroundColor: '#28a745', 
                        color: 'white', 
                        borderRadius: '8px', 
                        textDecoration: 'none',
                        fontWeight: 'bold' 
                    }}
                >
                    Entrar
                </Link>

                {/* Botão de Cadastro */}
                <Link 
                    to="/cadastro" 
                    style={{ 
                        padding: '12px 25px', 
                        border: '2px solid #28a745', 
                        color: '#28a745', 
                        borderRadius: '8px', 
                        textDecoration: 'none',
                        fontWeight: 'bold' 
                    }}
                >
                    Quero Me Cadastrar
                </Link>
            </div>
        </div>
    );
};

export default HomePage;