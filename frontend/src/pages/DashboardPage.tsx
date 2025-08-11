import React from 'react';
import { useAuth } from '../contexts/AuthContext';
// Simple icon components
const CreditCardIcon = () => <span>💳</span>;
const UserIcon = () => <span>👤</span>;
const ShieldCheckIcon = () => <span>🛡️</span>;
const ChartBarIcon = () => <span>📊</span>;

const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  const stats = [
    {
      name: 'Comptes actifs',
      value: '3',
      icon: CreditCardIcon,
      change: '+12%',
      changeType: 'increase',
    },
    {
      name: 'Transferts ce mois',
      value: '24',
      icon: ChartBarIcon,
      change: '+8%',
      changeType: 'increase',
    },
    {
      name: 'Statut KYC',
      value: user?.kycStatus || 'En attente',
      icon: ShieldCheckIcon,
      change: 'Complet',
      changeType: 'success',
    },
    {
      name: 'Niveau de risque',
      value: user?.riskLevel || 'Faible',
      icon: UserIcon,
      change: 'Stable',
      changeType: 'neutral',
    },
  ];

  const recentTransfers = [
    {
      id: '1',
      amount: '1,500.00 €',
      recipient: 'Jean Dupont',
      status: 'Complété',
      date: '2024-01-15',
    },
    {
      id: '2',
      amount: '750.00 €',
      recipient: 'Marie Martin',
      status: 'En cours',
      date: '2024-01-14',
    },
    {
      id: '3',
      amount: '2,300.00 €',
      recipient: 'Pierre Durand',
      status: 'Complété',
      date: '2024-01-13',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'complété':
        return 'bg-green-100 text-green-800';
      case 'en cours':
        return 'bg-yellow-100 text-yellow-800';
      case 'échec':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Tableau de bord
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Bienvenue, {user?.firstName} {user?.lastName}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div
            key={item.name}
            className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <item.icon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {item.name}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {item.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Transfers */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
            Transferts récents
          </h3>
          <div className="mt-4">
            <div className="flow-root">
              <ul className="-my-5 divide-y divide-gray-200 dark:divide-gray-700">
                {recentTransfers.map((transfer) => (
                  <li key={transfer.id} className="py-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {transfer.recipient}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {transfer.date}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {transfer.amount}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(transfer.status)}`}>
                          {transfer.status}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            <div className="mt-6">
              <a
                href="/transfers"
                className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-600"
              >
                Voir tous les transferts
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;