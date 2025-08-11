import React from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { 
  FiTrendingUp, 
  FiTrendingDown, 
  FiDollarSign, 
  FiCreditCard,
  FiSend,
  FiCheckCircle,
  FiXCircle,
  FiClock,
  FiShield
} from 'react-icons/fi';
import { Helmet } from 'react-helmet-async';
import { format } from 'date-fns';

import { useAuth } from '../hooks/useAuth';
import apiService from '../services/api';
import { DashboardStats, Transfer, TransferStatus } from '../types';
import StatCard from '../components/dashboard/StatCard';
import RecentTransfers from '../components/dashboard/RecentTransfers';
import TransferChart from '../components/dashboard/TransferChart';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  // Fetch dashboard data
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>(
    'dashboard-stats',
    apiService.getDashboardStats,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const { data: transfers, isLoading: transfersLoading } = useQuery<Transfer[]>(
    'recent-transfers',
    () => apiService.getTransfers({}, 1, 5).then(res => res.items),
    {
      refetchInterval: 30000,
    }
  );

  const { data: chartData, isLoading: chartLoading } = useQuery(
    'transfer-chart',
    () => apiService.getTransferChartData('7d'),
    {
      refetchInterval: 60000, // Refetch every minute
    }
  );

  if (statsLoading || transfersLoading || chartLoading) {
    return <LoadingSpinner />;
  }

  const getStatusIcon = (status: TransferStatus) => {
    switch (status) {
      case TransferStatus.COMPLETED:
        return <FiCheckCircle className="w-4 h-4 text-green-500" />;
      case TransferStatus.FAILED:
        return <FiXCircle className="w-4 h-4 text-red-500" />;
      case TransferStatus.PENDING:
      case TransferStatus.PROCESSING:
        return <FiClock className="w-4 h-4 text-yellow-500" />;
      default:
        return <FiSend className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: TransferStatus) => {
    switch (status) {
      case TransferStatus.COMPLETED:
        return 'text-green-600 bg-green-50';
      case TransferStatus.FAILED:
        return 'text-red-600 bg-red-50';
      case TransferStatus.PENDING:
      case TransferStatus.PROCESSING:
        return 'text-yellow-600 bg-yellow-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <>
      <Helmet>
        <title>Dashboard - Banking Transfer Platform</title>
      </Helmet>

      <div className="space-y-6">
        {/* Welcome Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-sm p-6"
        >
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.first_name}!
          </h1>
          <p className="text-gray-600">
            Here's what's happening with your transfers today.
          </p>
        </motion.div>

        {/* Statistics Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          <StatCard
            title="Total Transfers"
            value={stats?.total_transfers || 0}
            icon={<FiSend className="w-6 h-6" />}
            trend="up"
            trendValue="12%"
            color="blue"
          />
          
          <StatCard
            title="Total Amount"
            value={`$${(stats?.total_amount || 0).toLocaleString()}`}
            icon={<FiDollarSign className="w-6 h-6" />}
            trend="up"
            trendValue="8%"
            color="green"
          />
          
          <StatCard
            title="Pending Transfers"
            value={stats?.pending_transfers || 0}
            icon={<FiClock className="w-6 h-6" />}
            trend="down"
            trendValue="5%"
            color="yellow"
          />
          
          <StatCard
            title="Total Balance"
            value={`$${(stats?.total_balance || 0).toLocaleString()}`}
            icon={<FiCreditCard className="w-6 h-6" />}
            trend="up"
            trendValue="3%"
            color="purple"
          />
        </motion.div>

        {/* Charts and Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Transfer Chart */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-lg shadow-sm p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Transfer Activity (Last 7 Days)
            </h3>
            <TransferChart data={chartData || []} />
          </motion.div>

          {/* Recent Transfers */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg shadow-sm p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Recent Transfers
              </h3>
              <a
                href="/transfers"
                className="text-sm text-blue-600 hover:text-blue-500 transition-colors"
              >
                View all
              </a>
            </div>
            
            <div className="space-y-4">
              {transfers?.slice(0, 5).map((transfer) => (
                <motion.div
                  key={transfer.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(transfer.status)}
                    <div>
                      <p className="font-medium text-gray-900">
                        {transfer.beneficiary_name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {format(new Date(transfer.created_at), 'MMM dd, yyyy')}
                      </p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">
                      ${transfer.amount.toLocaleString()}
                    </p>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(transfer.status)}`}>
                      {transfer.status}
                    </span>
                  </div>
                </motion.div>
              ))}
              
              {(!transfers || transfers.length === 0) && (
                <div className="text-center py-8 text-gray-500">
                  <FiSend className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                  <p>No recent transfers</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-lg shadow-sm p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Quick Actions
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="flex items-center justify-center p-4 border-2 border-blue-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors">
              <FiSend className="w-5 h-5 text-blue-600 mr-2" />
              <span className="font-medium text-blue-600">New Transfer</span>
            </button>
            
            <button className="flex items-center justify-center p-4 border-2 border-green-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors">
              <FiCreditCard className="w-5 h-5 text-green-600 mr-2" />
              <span className="font-medium text-green-600">View Accounts</span>
            </button>
            
            <button className="flex items-center justify-center p-4 border-2 border-purple-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-colors">
              <FiShield className="w-5 h-5 text-purple-600 mr-2" />
              <span className="font-medium text-purple-600">KYC Status</span>
            </button>
          </div>
        </motion.div>
      </div>
    </>
  );
};

export default Dashboard;