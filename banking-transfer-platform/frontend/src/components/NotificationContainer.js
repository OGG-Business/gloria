import React from "react";
import { useNotification } from "../contexts/NotificationContext";

const NotificationContainer = ({ notifications }) => {
  const { removeNotification } = useNotification();

  const getIcon = (type) => {
    switch (type) {
      case "success":
        return "✅";
      case "error":
        return "⚠️";
      case "warning":
        return "⚠️";
      case "info":
        return "ℹ️";
      default:
        return "ℹ️";
    }
  };

  const getBackgroundColor = (type) => {
    switch (type) {
      case "success":
        return "bg-green-50 dark:bg-green-900";
      case "error":
        return "bg-red-50 dark:bg-red-900";
      case "warning":
        return "bg-yellow-50 dark:bg-yellow-900";
      case "info":
        return "bg-blue-50 dark:bg-blue-900";
      default:
        return "bg-gray-50 dark:bg-gray-900";
    }
  };

  const getBorderColor = (type) => {
    switch (type) {
      case "success":
        return "border-green-200 dark:border-green-700";
      case "error":
        return "border-red-200 dark:border-red-700";
      case "warning":
        return "border-yellow-200 dark:border-yellow-700";
      case "info":
        return "border-blue-200 dark:border-blue-700";
      default:
        return "border-gray-200 dark:border-gray-700";
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`max-w-sm w-full ${getBackgroundColor(notification.type)} border ${getBorderColor(notification.type)} rounded-lg shadow-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden`}
        >
          <div className="p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <span className="h-6 w-6">{getIcon(notification.type)}</span>
              </div>
              <div className="ml-3 w-0 flex-1 pt-0.5">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {notification.title}
                </p>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-300">
                  {notification.message}
                </p>
              </div>
              <div className="ml-4 flex-shrink-0 flex">
                <button
                  className="bg-transparent rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  onClick={() => removeNotification(notification.id)}
                >
                  <span className="sr-only">Fermer</span>
                  ✕
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default NotificationContainer;
