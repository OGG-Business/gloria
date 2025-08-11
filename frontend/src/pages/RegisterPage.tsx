import React from 'react';
import { useNavigate } from 'react-router-dom';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow sm:rounded-lg sm:px-10">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Inscription
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Cette fonctionnalité sera bientôt disponible.
        </p>
        <button
          onClick={() => navigate('/login')}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Retour à la connexion
        </button>
      </div>
    </div>
  );
};

export default RegisterPage;