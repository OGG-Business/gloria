import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';
import Keycloak from 'keycloak-js';

// Components
import { AuthProvider, useAuth } from './components/auth/AuthProvider';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Layout } from './components/common/Layout';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// Pages
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { TransfersPage } from './pages/TransfersPage';
import { TransferCreatePage } from './pages/TransferCreatePage';
import { TransferDetailPage } from './pages/TransferDetailPage';
import { AccountsPage } from './pages/AccountsPage';
import { KycPage } from './pages/KycPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { ProfilePage } from './pages/ProfilePage';
import { NotFoundPage } from './pages/NotFoundPage';

// Services
import { NotificationService } from './services/NotificationService';

// Styles
import './styles/globals.css';

// Configuration React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Configuration Keycloak
const keycloakConfig = {
  url: import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8180',
  realm: import.meta.env.VITE_KEYCLOAK_REALM || 'swiftpay',
  clientId: import.meta.env.VITE_OAUTH2_CLIENT_ID || 'swiftpay-frontend',
};

const keycloak = new Keycloak(keycloakConfig);

/**
 * Composant principal de l'application SwiftPay
 */
function App() {
  const [keycloakInitialized, setKeycloakInitialized] = useState(false);
  const [keycloakError, setKeycloakError] = useState<string | null>(null);

  useEffect(() => {
    // Initialisation de Keycloak
    keycloak
      .init({
        onLoad: 'check-sso',
        silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
        pkceMethod: 'S256',
        checkLoginIframe: false, // Désactivé pour éviter les problèmes CORS en dev
      })
      .then((authenticated) => {
        setKeycloakInitialized(true);
        console.log('Keycloak initialisé. Authentifié:', authenticated);
        
        // Initialiser les notifications WebSocket si authentifié
        if (authenticated) {
          NotificationService.initialize();
        }
      })
      .catch((error) => {
        console.error('Erreur lors de l\'initialisation de Keycloak:', error);
        setKeycloakError('Erreur de connexion au service d\'authentification');
        setKeycloakInitialized(true);
      });

    // Nettoyage
    return () => {
      NotificationService.disconnect();
    };
  }, []);

  if (!keycloakInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600">Initialisation de l'authentification...</p>
        </div>
      </div>
    );
  }

  if (keycloakError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <h2 className="font-bold">Erreur d'authentification</h2>
            <p>{keycloakError}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-2 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
            >
              Réessayer
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider keycloak={keycloak}>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <AppRoutes />
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#4ade80',
                    secondary: '#fff',
                  },
                },
                error: {
                  duration: 5000,
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </div>
        </Router>
      </AuthProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

/**
 * Configuration des routes de l'application
 */
function AppRoutes() {
  const { isAuthenticated, user } = useAuth();

  return (
    <Routes>
      {/* Route publique de connexion */}
      <Route 
        path="/login" 
        element={!isAuthenticated ? <LoginPage /> : <Navigate to="/dashboard" replace />} 
      />
      
      {/* Routes protégées */}
      <Route path="/" element={<ProtectedRoute />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        <Route element={<Layout />}>
          {/* Dashboard principal */}
          <Route path="/dashboard" element={<DashboardPage />} />
          
          {/* Gestion des transferts */}
          <Route path="/transfers" element={<TransfersPage />} />
          <Route path="/transfers/new" element={<TransferCreatePage />} />
          <Route path="/transfers/:id" element={<TransferDetailPage />} />
          
          {/* Gestion des comptes */}
          <Route path="/accounts" element={<AccountsPage />} />
          
          {/* KYC/Vérification */}
          <Route path="/kyc" element={<KycPage />} />
          
          {/* Profil utilisateur */}
          <Route path="/profile" element={<ProfilePage />} />
          
          {/* Administration (admin/operator uniquement) */}
          {user?.role === 'ADMIN' || user?.role === 'OPERATOR' ? (
            <Route path="/admin/*" element={<AdminDashboardPage />} />
          ) : null}
        </Route>
      </Route>
      
      {/* Route 404 */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

export default App;