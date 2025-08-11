import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
// Simple icon components
const HomeIcon = () => <span>🏠</span>;
const CreditCardIcon = () => <span>💳</span>;
const UserIcon = () => <span>👤</span>;
const CogIcon = () => <span>⚙️</span>;
const ShieldCheckIcon = () => <span>🛡️</span>;
const ChartBarIcon = () => <span>📊</span>;
const MenuIcon = () => <span>☰</span>;
const XIcon = () => <span>✕</span>;

const Sidebar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const { user } = useAuth();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Transfers', href: '/transfers', icon: CreditCardIcon },
    { name: 'Accounts', href: '/accounts', icon: UserIcon },
    { name: 'KYC', href: '/kyc', icon: ShieldCheckIcon },
    { name: 'Profile', href: '/profile', icon: CogIcon },
  ];

  const adminNavigation = [
    { name: 'Admin', href: '/admin', icon: ChartBarIcon },
  ];

  const isActive = (href: string) => location.pathname === href;

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
        >
          {isOpen ? (
            <XIcon className="h-6 w-6" />
          ) : (
            <MenuIcon className="h-6 w-6" />
          )}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-gray-800 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-center h-16 bg-gray-900">
          <h1 className="text-white text-xl font-bold">Banking Platform</h1>
        </div>
        
        <nav className="mt-8">
          <div className="px-2 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  group flex items-center px-2 py-2 text-sm font-medium rounded-md
                  ${isActive(item.href)
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }
                `}
                onClick={() => setIsOpen(false)}
              >
                <item.icon
                  className={`
                    mr-3 h-6 w-6
                    ${isActive(item.href)
                      ? 'text-white'
                      : 'text-gray-400 group-hover:text-gray-300'
                    }
                  `}
                />
                {item.name}
              </Link>
            ))}

            {/* Admin navigation */}
            {user?.roles?.includes('ADMIN') && (
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
                    className={`
                      group flex items-center px-2 py-2 text-sm font-medium rounded-md
                      ${isActive(item.href)
                        ? 'bg-gray-900 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                      }
                    `}
                    onClick={() => setIsOpen(false)}
                  >
                    <item.icon
                      className={`
                        mr-3 h-6 w-6
                        ${isActive(item.href)
                          ? 'text-white'
                          : 'text-gray-400 group-hover:text-gray-300'
                        }
                      `}
                    />
                    {item.name}
                  </Link>
                ))}
              </>
            )}
          </div>
        </nav>
      </div>

      {/* Overlay for mobile */}
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