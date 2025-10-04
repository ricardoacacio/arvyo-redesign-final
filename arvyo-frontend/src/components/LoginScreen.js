// src/components/LoginScreen.js

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext'; // Importa o hook de autenticação

function LoginScreen() {
  const { loginUser } = useAuth(); // Pega a função de login do contexto
  const [username, setUsername] = useState('seu_admin'); // Dica: use o superuser do Django
  const [password, setPassword] = useState('sua_senha');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      await loginUser(username, password);
    } catch (err) {
      // O erro 400 (Bad Request) geralmente é senha/usuário errado
      if (err.response && err.response.status === 400) {
        setError('Credenciais inválidas. Verifique seu usuário e senha.');
      } else {
        setError('Ocorreu um erro inesperado. Tente novamente.');
        console.error("Erro completo:", err);
      }
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '300px', margin: '50px auto', border: '1px solid #ccc' }}>
      <h2>Login para Arvyo</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label>Usuário:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label>Senha:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
        {error && <p style={{ color: 'red', marginBottom: '15px' }}>{error}</p>}
        <button type="submit" style={{ width: '100%', padding: '10px', background: 'green', color: 'white', border: 'none' }}>
          Entrar
        </button>
      </form>
    </div>
  );
}

export default LoginScreen;