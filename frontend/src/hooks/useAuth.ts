import { useState, useEffect, createContext, useContext } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';

import apiService from '../services/api';
import { User, LoginRequest } from '../types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const queryClient = useQueryClient();

  // Check if user is authenticated on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  // Fetch current user
  const { data: user, isLoading, refetch } = useQuery<User>(
    'current-user',
    apiService.getCurrentUser,
    {
      enabled: isAuthenticated,
      retry: false,
      onError: () => {
        // Token is invalid, clear auth state
        setIsAuthenticated(false);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      }
    }
  );

  // Login mutation
  const loginMutation = useMutation(
    (credentials: LoginRequest) => apiService.login(credentials),
    {
      onSuccess: (response) => {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        setIsAuthenticated(true);
        queryClient.setQueryData('current-user', response.user);
        toast.success('Login successful!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Login failed');
        throw error;
      }
    }
  );

  // Logout mutation
  const logoutMutation = useMutation(
    () => apiService.logout(),
    {
      onSuccess: () => {
        setIsAuthenticated(false);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        queryClient.clear();
        toast.success('Logged out successfully');
      },
      onError: () => {
        // Even if logout fails, clear local state
        setIsAuthenticated(false);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        queryClient.clear();
      }
    }
  );

  const login = async (credentials: LoginRequest) => {
    await loginMutation.mutateAsync(credentials);
  };

  const logout = async () => {
    await logoutMutation.mutateAsync();
  };

  const refreshUser = () => {
    refetch();
  };

  const value: AuthContextType = {
    user: user || null,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};