// src/pages/Login/Login.js
import React, { useState } from 'react';
import { useNavigate, Link, Navigate } from 'react-router-dom';     
import { useAuth } from '../../context/AuthContext'; 

const LoginPage = () => {
    // Hooks para gerenciar o estado do formulário e o status
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Hooks do React Router e do Context
    const navigate = useNavigate();
    const { loginUser, isLoggedIn } = useAuth(); // Usa a função de login do seu Context

    // Se o usuário JÁ estiver logado, redireciona imediatamente para o Dashboard
    if (isLoggedIn) {
        // Redireciona para o Dashboard
        return <Navigate to="/dashboard" replace />;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        if (!username || !password) {
            setError('Por favor, preencha todos os campos.');
            return;
        }

        setIsSubmitting(true);

        try {
            // Chama a função loginUser do AuthContext, que lida com a API
            const success = await loginUser(username, password);
            
            if (success) {
                // Navegação para a área protegida após o login bem-sucedido
                navigate('/dashboard', { replace: true });
            }

        } catch (err) {
            // Captura erros de credenciais inválidas (geralmente 400 ou 403)
            // Lembre-se, o Django retorna 200 em caso de sucesso no POST /auth/login/
            console.error("Erro completo:", err);
            // Mensagem de erro padrão para credenciais erradas
            setError('Credenciais inválidas. Verifique seu usuário e senha.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
            <h2>Entrar no Arvyo</h2>
            
            <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '15px' }}>
                
                {/* Campo Usuário */}
                <div>
                    <label>Usuário:</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        disabled={isSubmitting}
                        style={{ width: '100%', padding: '10px', marginTop: '5px' }}
                    />
                </div>

                {/* Campo Senha */}
                <div>
                    <label>Senha:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={isSubmitting}
                        style={{ width: '100%', padding: '10px', marginTop: '5px' }}
                    />
                </div>

                {/* Mensagem de Erro */}
                {error && <p style={{ color: 'red', margin: 0 }}>{error}</p>}

                {/* Botão de Envio */}
                <button 
                    type="submit" 
                    disabled={isSubmitting}
                    style={{ padding: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
                >
                    {isSubmitting ? 'Aguarde...' : 'Fazer Login'}
                </button>
            </form>

            <p style={{ marginTop: '20px', textAlign: 'center' }}>
                Não tem conta? <Link to="/cadastro">Cadastre-se aqui</Link>
            </p>
        </div>
    );
};

export default LoginPage;