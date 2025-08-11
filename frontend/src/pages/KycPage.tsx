import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const KycPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          KYC - Know Your Customer
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Vérification d'identité et conformité
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Statut KYC: {user?.kycStatus || 'En attente'}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Cette fonctionnalité sera bientôt disponible.
          </p>
        </div>
      </div>
    </div>
  );
};

export default KycPage;