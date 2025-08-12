import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import styled from 'styled-components';

// Components
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import TransferForm from './pages/TransferForm';
import TransferHistory from './pages/TransferHistory';
import AccountManagement from './pages/AccountManagement';
import KYCPortal from './pages/KYCPortal';
import AdminPanel from './pages/AdminPanel';
import Login from './pages/Login';
import Register from './pages/Register';

// Styles
const AppContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
`;

const ContentArea = styled.div`
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
`;

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
      <Router>
        <AppContainer>
          <Sidebar />
          <MainContent>
            <Header />
            <ContentArea>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/" element={<Dashboard />} />
                <Route path="/transfer/new" element={<TransferForm />} />
                <Route path="/transfers" element={<TransferHistory />} />
                <Route path="/accounts" element={<AccountManagement />} />
                <Route path="/kyc" element={<KYCPortal />} />
                <Route path="/admin" element={<AdminPanel />} />
              </Routes>
            </ContentArea>
          </MainContent>
        </AppContainer>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </Router>
    </QueryClientProvider>
  );
}

export default App;