import React from 'react';

const Sidebar: React.FC = () => {
  return (
    <aside style={{ width: '250px', background: 'white', borderRight: '1px solid #e2e8f0' }}>
      <div style={{ padding: '2rem' }}>
        <h2>Navigation</h2>
        <ul>
          <li>Dashboard</li>
          <li>Transferts</li>
          <li>Comptes</li>
          <li>KYC</li>
          <li>Admin</li>
        </ul>
      </div>
    </aside>
  );
};

export default Sidebar;
