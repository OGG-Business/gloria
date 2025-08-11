import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import Keycloak from 'keycloak-js';
import toast from 'react-hot-toast';

// Types
interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'USER' | 'OPERATOR' | 'ADMIN';
  mfaEnabled: boolean;
  kycStatus?: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  token: string | null;
  login: () => void;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
  keycloak: Keycloak;
}

/**
 * Provider d'authentification avec Keycloak
 * Gère l'état d'authentification, les tokens et les informations utilisateur
 */
export function AuthProvider({ children, keycloak }: AuthProviderProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (keycloak.authenticated) {
          setIsAuthenticated(true);
          setToken(keycloak.token || null);
          
          // Charger les informations utilisateur
          await loadUserProfile();
          
          // Configuration du rafraîchissement automatique des tokens
          setupTokenRefresh();
        }
      } catch (error) {
        console.error('Erreur lors de l\'initialisation de l\'authentification:', error);
        toast.error('Erreur d\'authentification');
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, [keycloak]);

  /**
   * Charge le profil utilisateur depuis Keycloak et l'API backend
   */
  const loadUserProfile = async () => {
    try {
      // Charger le profil Keycloak
      const profile = await keycloak.loadUserProfile();
      
      // Extraire les rôles
      const roles = keycloak.tokenParsed?.realm_access?.roles || [];
      const userRole = roles.includes('admin') ? 'ADMIN' : 
                      roles.includes('operator') ? 'OPERATOR' : 'USER';

      // Créer l'objet utilisateur
      const userData: User = {
        id: profile.id || keycloak.subject || '',
        email: profile.email || '',
        firstName: profile.firstName || '',
        lastName: profile.lastName || '',
        role: userRole,
        mfaEnabled: false, // À récupérer depuis l'API backend
      };

      setUser(userData);
      
      // Charger les informations supplémentaires depuis l'API backend
      await loadBackendUserInfo(userData.id);
      
    } catch (error) {
      console.error('Erreur lors du chargement du profil utilisateur:', error);
      toast.error('Erreur lors du chargement du profil');
    }
  };

  /**
   * Charge les informations utilisateur depuis l'API backend
   */
  const loadBackendUserInfo = async (userId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${keycloak.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const backendUserInfo = await response.json();
        setUser(prevUser => prevUser ? {
          ...prevUser,
          mfaEnabled: backendUserInfo.mfaEnabled,
          kycStatus: backendUserInfo.kycStatus,
        } : null);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des infos backend:', error);
      // Ne pas afficher d'erreur car ce n'est pas critique
    }
  };

  /**
   * Configure le rafraîchissement automatique des tokens
   */
  const setupTokenRefresh = () => {
    // Rafraîchir le token toutes les 5 minutes
    const refreshInterval = setInterval(async () => {
      try {
        const refreshed = await keycloak.updateToken(30); // Rafraîchir si expire dans 30s
        if (refreshed) {
          setToken(keycloak.token || null);
          console.log('Token rafraîchi automatiquement');
        }
      } catch (error) {
        console.error('Erreur lors du rafraîchissement du token:', error);
        logout();
      }
    }, 5 * 60 * 1000); // 5 minutes

    // Nettoyage
    return () => clearInterval(refreshInterval);
  };

  /**
   * Connexion utilisateur
   */
  const login = () => {
    keycloak.login({
      redirectUri: window.location.origin + '/dashboard',
    });
  };

  /**
   * Déconnexion utilisateur
   */
  const logout = () => {
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
    
    keycloak.logout({
      redirectUri: window.location.origin + '/login',
    });
  };

  /**
   * Rafraîchissement manuel du token
   */
  const refreshToken = async (): Promise<boolean> => {
    try {
      const refreshed = await keycloak.updateToken(-1); // Force refresh
      if (refreshed && keycloak.token) {
        setToken(keycloak.token);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Erreur lors du rafraîchissement du token:', error);
      return false;
    }
  };

  /**
   * Vérifie si l'utilisateur a un rôle spécifique
   */
  const hasRole = (role: string): boolean => {
    if (!user) return false;
    
    // Admin a tous les droits
    if (user.role === 'ADMIN') return true;
    
    // Operator a les droits USER
    if (user.role === 'OPERATOR' && role === 'USER') return true;
    
    return user.role === role;
  };

  /**
   * Vérifie si l'utilisateur a au moins un des rôles spécifiés
   */
  const hasAnyRole = (roles: string[]): boolean => {
    return roles.some(role => hasRole(role));
  };

  const contextValue: AuthContextType = {
    isAuthenticated,
    isLoading,
    user,
    token,
    login,
    logout,
    refreshToken,
    hasRole,
    hasAnyRole,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook pour utiliser le contexte d'authentification
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
}

/**
 * Composant principal avec providers
 */
function SwiftPayApp() {
  return (
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default SwiftPayApp;