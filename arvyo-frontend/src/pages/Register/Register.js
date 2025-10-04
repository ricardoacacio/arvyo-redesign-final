// src/pages/Register/Register.js (Implementação Final do Formulário)
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext'; // Importar useAuth

const RegisterPage = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const navigate = useNavigate();

    // Pega a função de registro do Contexto
    const { registerUser } = useAuth(); 

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('As senhas não coincidem.');
            return;
        }
        
        if (!username || !email || !password || !confirmPassword) {
            setError('Por favor, preencha todos os campos.');
            return;
        }

        setIsSubmitting(true);
        
        try {
            // Chama a função real de registro que envia dados para /api/auth/register/
            await registerUser(username, email, password);
            
            // Sucesso: Alerta e redireciona para a tela de Login
            alert('Cadastro realizado com sucesso! Agora você pode fazer o login.');
            navigate('/login', { replace: true });
            
        } catch (err) {
            // Captura erros da API (usuário já existente, senha fraca, etc.)
            let errorMessage = 'Erro ao cadastrar. Verifique os dados.';
            
            // Tentativa de extrair a mensagem de erro detalhada do Django
            if (err.response && err.response.data) {
                const data = err.response.data;
                // Procura por campos de erro comuns no Django
                if (data.username) {
                    errorMessage = data.username[0];
                } else if (data.email) {
                    errorMessage = data.email[0];
                } else if (data.detalhe) {
                    errorMessage = data.detalhe;
                }
            }

            setError(errorMessage);

        } finally {
            setIsSubmitting(false);
        }
    };
    
    return (
        <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
            <h2>Criar Conta no Arvyo</h2>
            
            <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '15px' }}>
                
                {/* Campo Usuário */}
                <div>
                    <label>Usuário:</label>
                    <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} disabled={isSubmitting} style={{ width: '100%', padding: '10px', marginTop: '5px' }} />
                </div>

                {/* Campo Email */}
                <div>
                    <label>Email:</label>
                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} disabled={isSubmitting} style={{ width: '100%', padding: '10px', marginTop: '5px' }} />
                </div>

                {/* Campo Senha */}
                <div>
                    <label>Senha:</label>
                    <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} disabled={isSubmitting} style={{ width: '100%', padding: '10px', marginTop: '5px' }} />
                </div>

                {/* Campo Confirmação Senha */}
                <div>
                    <label>Confirmar Senha:</label>
                    <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} disabled={isSubmitting} style={{ width: '100%', padding: '10px', marginTop: '5px' }} />
                </div>

                {/* Mensagem de Erro */}
                {error && <p style={{ color: 'red', margin: 0 }}>{error}</p>}

                {/* Botão de Envio */}
                <button type="submit" disabled={isSubmitting} style={{ padding: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
                    {isSubmitting ? 'Cadastrando...' : 'Cadastrar'}
                </button>
            </form>

            <p style={{ marginTop: '20px', textAlign: 'center' }}>
                Já tem conta? <Link to="/login">Fazer Login</Link>
            </p>
        </div>
    );
};

export default RegisterPage;