import React from 'react';

const AdminPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Administration
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Interface d'administration
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Fonctionnalité en développement
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            L'interface d'administration sera bientôt disponible.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;