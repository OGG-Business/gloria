import React from "react";
import { useAuth } from "../contexts/AuthContext";

const Header = ({ user, theme, onThemeToggle }) => {
  const { logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              Plateforme de Transferts Bancaires
            </h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={onThemeToggle}
              className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
            >
              {theme === "dark" ? "☀️" : "🌙"}
            </button>

            <div className="relative">
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <span className="h-5 w-5 text-gray-400">👤</span>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {user?.firstName} {user?.lastName}
                  </span>
                </div>
                
                <button
                  onClick={handleLogout}
                  className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                  title="Se déconnecter"
                >
                  🚪
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
