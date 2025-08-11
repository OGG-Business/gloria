import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const { user } = useAuth();

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: "🏠" },
    { name: "Transfers", href: "/transfers", icon: "💳" },
    { name: "Accounts", href: "/accounts", icon: "👤" },
    { name: "KYC", href: "/kyc", icon: "🛡️" },
    { name: "Profile", href: "/profile", icon: "⚙️" },
  ];

  const adminNavigation = [
    { name: "Admin", href: "/admin", icon: "📊" },
  ];

  const isActive = (href) => location.pathname === href;

  return (
    <>
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
        >
          {isOpen ? "✕" : "☰"}
        </button>
      </div>

      <div className={`fixed inset-y-0 left-0 z-40 w-64 bg-gray-800 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${isOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex items-center justify-center h-16 bg-gray-900">
          <h1 className="text-white text-xl font-bold">Banking Platform</h1>
        </div>
        
        <nav className="mt-8">
          <div className="px-2 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${isActive(item.href) ? "bg-gray-900 text-white" : "text-gray-300 hover:bg-gray-700 hover:text-white"}`}
                onClick={() => setIsOpen(false)}
              >
                <span className="mr-3 h-6 w-6">{item.icon}</span>
                {item.name}
              </Link>
            ))}

            {user?.roles?.includes("ADMIN") && (
              <>
                <div className="pt-4 pb-2 border-t border-gray-700">
                  <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Administration
                  </h3>
                </div>
                {adminNavigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${isActive(item.href) ? "bg-gray-900 text-white" : "text-gray-300 hover:bg-gray-700 hover:text-white"}`}
                    onClick={() => setIsOpen(false)}
                  >
                    <span className="mr-3 h-6 w-6">{item.icon}</span>
                    {item.name}
                  </Link>
                ))}
              </>
            )}
          </div>
        </nav>
      </div>

      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
};

export default Sidebar;
