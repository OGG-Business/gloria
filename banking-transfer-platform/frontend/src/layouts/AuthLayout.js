import React from "react";
import { useTheme } from "../contexts/ThemeContext";
import { useNotification } from "../contexts/NotificationContext";
import NotificationContainer from "../components/NotificationContainer";

const AuthLayout = ({ children }) => {
  const { theme } = useTheme();
  const { notifications } = useNotification();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Banking Transfer Platform
          </h2>
        </div>
        {children}
      </div>
      <NotificationContainer notifications={notifications} />
    </div>
  );
};

export default AuthLayout;
