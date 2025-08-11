import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "react-query";
import { AuthProvider } from "./contexts/AuthContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { NotificationProvider } from "./contexts/NotificationContext";
import MainLayout from "./layouts/MainLayout";
import AuthLayout from "./layouts/AuthLayout";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import TransfersPage from "./pages/TransfersPage";
import AccountsPage from "./pages/AccountsPage";
import ProfilePage from "./pages/ProfilePage";
import KycPage from "./pages/KycPage";
import AdminPage from "./pages/AdminPage";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";
import "./styles/global.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <NotificationProvider>
          <AuthProvider>
            <Router>
              <div className="App">
                <Routes>
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
                  <Route path="/accounts" element={
                    <ProtectedRoute>
                      <MainLayout>
                        <AccountsPage />
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
                  <Route path="/admin" element={
                    <AdminRoute>
                      <MainLayout>
                        <AdminPage />
                      </MainLayout>
                    </AdminRoute>
                  } />
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </div>
            </Router>
          </AuthProvider>
        </NotificationProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
