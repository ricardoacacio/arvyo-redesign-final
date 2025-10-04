// src/App.js
import React from 'react';
import { AuthProvider } from './context/AuthContext'; // NOVO: Importa o Provedor
import Dashboard from './components/Dashboard';

function App() {
  // O Dashboard e qualquer outro componente dentro de <AuthProvider>
  // agora podem acessar o estado de login e as funções login/logout.
  return (
    <AuthProvider> 
      <div className="App">
        <header style={{padding: '20px', backgroundColor: '#f0f0f0'}}>
          <h1>Arvyo - Teste de Integração</h1>
        </header>
        <Dashboard />
      </div>
    </AuthProvider>
  );
}

export default App;