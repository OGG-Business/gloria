import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { NotificationProvider } from './contexts/NotificationContext';

// Layouts
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import TransfersPage from './pages/transfers/TransfersPage';
import TransferCreatePage from './pages/transfers/TransferCreatePage';
import TransferDetailsPage from './pages/transfers/TransferDetailsPage';
import AccountsPage from './pages/accounts/AccountsPage';
import AccountDetailsPage from './pages/accounts/AccountDetailsPage';
import ProfilePage from './pages/ProfilePage';
import KycPage from './pages/KycPage';
import AdminPage from './pages/admin/AdminPage';

// Components
import LoadingSpinner from './components/common/LoadingSpinner';
import NotificationContainer from './components/common/NotificationContainer';

// Styles
import './styles/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Admin Route Component
const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!user?.roles?.includes('ADMIN')) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <NotificationProvider>
            <Router>
              <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
                <Routes>
                  {/* Public Routes */}
                  <Route path="/login" element={
                    <AuthLayout>
                      <LoginPage />
                    </AuthLayout>
                  } />
                  <Route path="/register" element={
                    <AuthLayout>
                      <RegisterPage />
                    </AuthLayout>
                  } />

                  {/* Protected Routes */}
                  <Route path="/" element={
                    <ProtectedRoute>
                      <MainLayout>
                        <DashboardPage />
                      </MainLayout>
                    </ProtectedRoute>
                  } />

                  <Route path="/dashboard" element={
                    <ProtectedRoute>
                      <MainLayout>
                        <DashboardPage />
                      </MainLayout>
                    </ProtectedRoute>
                  } />

                  <Route path="/transfers" element={
                    <ProtectedRoute>
                      <MainLayout>
                        <TransfersPage />
                      </MainLayout>
                    </ProtectedRoute>
                  } />

                  <Route path="/transfers/create" element={
                    <ProtectedRoute>
                      <MainLayout>
                        <TransferCreatePage />
                      </MainLayout>
                    </ProtectedRoute>
                  } />

                  <Route path="/transfers/:id" element={
                    <ProtectedRoute>
                      <MainLayout>
                        <TransferDetailsPage />
                      </MainLayout>
                    </ProtectedRoute>
                  } />

                  <Route path="/accounts" element={
                    <ProtectedRoute>
                      <MainLayout>
                        <AccountsPage />
                      </MainLayout>
                    </ProtectedRoute>
                  } />

                  <Route path="/accounts/:id" element={
                    <ProtectedRoute>
                      <MainLayout>
                        <AccountDetailsPage />
                      </MainLayout>
                    </ProtectedRoute>
                  } />

                  <Route path="/profile" element={
                    <ProtectedRoute>
                      <MainLayout>
                        <ProfilePage />
                      </MainLayout>
                    </ProtectedRoute>
                  } />

                  <Route path="/kyc" element={
                    <ProtectedRoute>
                      <MainLayout>
                        <KycPage />
                      </MainLayout>
                    </ProtectedRoute>
                  } />

                  {/* Admin Routes */}
                  <Route path="/admin" element={
                    <AdminRoute>
                      <MainLayout>
                        <AdminPage />
                      </MainLayout>
                    </AdminRoute>
                  } />

                  {/* 404 Route */}
                  <Route path="*" element={
                    <Navigate to="/dashboard" replace />
                  } />
                </Routes>

                <NotificationContainer />
              </div>
            </Router>
          </NotificationProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;