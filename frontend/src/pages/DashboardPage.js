import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const DashboardPage = () => {
  const { user } = useAuth();

  const stats = [
    {
      name: 'Comptes actifs',
      value: '3',
      icon: '💳',
    },
    {
      name: 'Transferts ce mois',
      value: '24',
      icon: '📊',
    },
    {
      name: 'Statut KYC',
      value: user?.kycStatus || 'En attente',
      icon: '🛡️',
    },
    {
      name: 'Niveau de risque',
      value: user?.riskLevel || 'Faible',
      icon: '👤',
    },
  ];

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

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div
            key={item.name}
            className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <span className="h-6 w-6">{item.icon}</span>
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

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
            Transferts récents
          </h3>
          <div className="mt-4">
            <p className="text-gray-600 dark:text-gray-400">
              Aucun transfert récent
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;