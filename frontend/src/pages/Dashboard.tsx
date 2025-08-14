import React from 'react';
import styled from 'styled-components';
import { FiTrendingUp, FiTrendingDown, FiDollarSign, FiUsers } from 'react-icons/fi';
import { useQuery } from 'react-query';
import axios from 'axios';

const DashboardContainer = styled.div`
  padding: 2rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 2rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const StatHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const StatTitle = styled.h3`
  font-size: 0.875rem;
  font-weight: 600;
  color: #718096;
  margin: 0;
`;

const StatIcon = styled.div<{ color: string }>`
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: ${props => props.color};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
`;

const StatChange = styled.div<{ isPositive: boolean }>`
  font-size: 0.875rem;
  color: ${props => props.isPositive ? '#38a169' : '#e53e3e'};
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
`;

const ChartCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const ChartTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
`;

const RecentTransfersCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const TransferItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #e2e8f0;

  &:last-child {
    border-bottom: none;
  }
`;

const TransferInfo = styled.div`
  flex: 1;
`;

const TransferAmount = styled.div<{ type: 'in' | 'out' }>`
  font-weight: 600;
  color: ${props => props.type === 'in' ? '#38a169' : '#e53e3e'};
`;

const TransferStatus = styled.span<{ status: string }>`
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background: ${props => {
    switch (props.status) {
      case 'completed': return '#c6f6d5';
      case 'pending': return '#fef5e7';
      case 'failed': return '#fed7d7';
      default: return '#e2e8f0';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'completed': return '#22543d';
      case 'pending': return '#744210';
      case 'failed': return '#742a2a';
      default: return '#4a5568';
    }
  }};
`;

const Dashboard: React.FC = () => {
  const { data: stats } = useQuery('dashboard-stats', async () => {
    const response = await axios.get('/admin/stats');
    return response.data;
  });

  const { data: recentTransfers } = useQuery('recent-transfers', async () => {
    const response = await axios.get('/transfers?limit=5');
    return response.data;
  });

  const mockStats = {
    totalTransfers: 1247,
    totalAmount: 2847500,
    activeUsers: 89,
    successRate: 98.5,
    transfersChange: 12.5,
    amountChange: -2.3,
    usersChange: 5.7,
    successChange: 1.2
  };

  const mockTransfers = [
    {
      id: '1',
      amount: 50000,
      currency: 'USD',
      recipient: 'John Doe',
      status: 'completed',
      date: '2024-01-15T10:30:00Z'
    },
    {
      id: '2',
      amount: 25000,
      currency: 'EUR',
      recipient: 'Jane Smith',
      status: 'pending',
      date: '2024-01-15T09:15:00Z'
    },
    {
      id: '3',
      amount: 75000,
      currency: 'CDF',
      recipient: 'Bob Johnson',
      status: 'completed',
      date: '2024-01-15T08:45:00Z'
    }
  ];

  return (
    <DashboardContainer>
      <Title>Tableau de bord</Title>

      <StatsGrid>
        <StatCard>
          <StatHeader>
            <StatTitle>Total Transferts</StatTitle>
            <StatIcon color="#3182ce">
              <FiTrendingUp size={20} />
            </StatIcon>
          </StatHeader>
          <StatValue>{mockStats.totalTransfers.toLocaleString()}</StatValue>
          <StatChange isPositive={mockStats.transfersChange > 0}>
            {mockStats.transfersChange > 0 ? <FiTrendingUp size={14} /> : <FiTrendingDown size={14} />}
            {Math.abs(mockStats.transfersChange)}% ce mois
          </StatChange>
        </StatCard>

        <StatCard>
          <StatHeader>
            <StatTitle>Montant Total</StatTitle>
            <StatIcon color="#38a169">
              <FiDollarSign size={20} />
            </StatIcon>
          </StatHeader>
          <StatValue>${(mockStats.totalAmount / 1000000).toFixed(1)}M</StatValue>
          <StatChange isPositive={mockStats.amountChange > 0}>
            {mockStats.amountChange > 0 ? <FiTrendingUp size={14} /> : <FiTrendingDown size={14} />}
            {Math.abs(mockStats.amountChange)}% ce mois
          </StatChange>
        </StatCard>

        <StatCard>
          <StatHeader>
            <StatTitle>Utilisateurs Actifs</StatTitle>
            <StatIcon color="#d69e2e">
              <FiUsers size={20} />
            </StatIcon>
          </StatHeader>
          <StatValue>{mockStats.activeUsers}</StatValue>
          <StatChange isPositive={mockStats.usersChange > 0}>
            {mockStats.usersChange > 0 ? <FiTrendingUp size={14} /> : <FiTrendingDown size={14} />}
            {Math.abs(mockStats.usersChange)}% ce mois
          </StatChange>
        </StatCard>

        <StatCard>
          <StatHeader>
            <StatTitle>Taux de Réussite</StatTitle>
            <StatIcon color="#38a169">
              <FiTrendingUp size={20} />
            </StatIcon>
          </StatHeader>
          <StatValue>{mockStats.successRate}%</StatValue>
          <StatChange isPositive={mockStats.successChange > 0}>
            {mockStats.successChange > 0 ? <FiTrendingUp size={14} /> : <FiTrendingDown size={14} />}
            {Math.abs(mockStats.successChange)}% ce mois
          </StatChange>
        </StatCard>
      </StatsGrid>

      <ContentGrid>
        <ChartCard>
          <ChartTitle>Évolution des Transferts</ChartTitle>
          <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#718096' }}>
            Graphique des transferts (Intégration Chart.js/Recharts)
          </div>
        </ChartCard>

        <RecentTransfersCard>
          <ChartTitle>Transferts Récents</ChartTitle>
          {mockTransfers.map((transfer) => (
            <TransferItem key={transfer.id}>
              <TransferInfo>
                <div style={{ fontWeight: 500, color: '#2d3748' }}>
                  {transfer.recipient}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#718096' }}>
                  {new Date(transfer.date).toLocaleDateString()}
                </div>
              </TransferInfo>
              <div style={{ textAlign: 'right' }}>
                <TransferAmount type={transfer.status === 'completed' ? 'in' : 'out'}>
                  {transfer.amount.toLocaleString()} {transfer.currency}
                </TransferAmount>
                <TransferStatus status={transfer.status}>
                  {transfer.status === 'completed' ? 'Terminé' : 
                   transfer.status === 'pending' ? 'En cours' : 'Échoué'}
                </TransferStatus>
              </div>
            </TransferItem>
          ))}
        </RecentTransfersCard>
      </ContentGrid>
    </DashboardContainer>
  );
};

export default Dashboard;