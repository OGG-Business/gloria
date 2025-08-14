import React from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { 
  FiHome, 
  FiSend, 
  FiList, 
  FiCreditCard, 
  FiShield, 
  FiSettings,
  FiTrendingUp,
  FiUsers
} from 'react-icons/fi';

const SidebarContainer = styled.aside`
  width: 280px;
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
`;

const Logo = styled.div`
  padding: 2rem;
  border-bottom: 1px solid #e2e8f0;
  text-align: center;

  h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #2d3748;
    margin: 0;
  }

  p {
    font-size: 0.8rem;
    color: #718096;
    margin: 0.25rem 0 0 0;
  }
`;

const Nav = styled.nav`
  flex: 1;
  padding: 1rem 0;
`;

const NavSection = styled.div`
  margin-bottom: 2rem;

  h3 {
    font-size: 0.75rem;
    font-weight: 600;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0 2rem;
    margin-bottom: 0.5rem;
  }
`;

const NavItem = styled(NavLink)`
  display: flex;
  align-items: center;
  padding: 0.75rem 2rem;
  color: #4a5568;
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;

  &:hover {
    background: #f7fafc;
    color: #2d3748;
  }

  &.active {
    background: #ebf8ff;
    color: #3182ce;
    border-left-color: #3182ce;
  }

  svg {
    margin-right: 0.75rem;
    width: 20px;
    height: 20px;
  }
`;

const Footer = styled.div`
  padding: 1rem 2rem;
  border-top: 1px solid #e2e8f0;
  text-align: center;

  p {
    font-size: 0.75rem;
    color: #a0aec0;
    margin: 0;
  }
`;

const Sidebar: React.FC = () => {
  return (
    <SidebarContainer>
      <Logo>
        <h1>Banking Transfer</h1>
        <p>Plateforme de Transferts</p>
      </Logo>

      <Nav>
        <NavSection>
          <h3>Principal</h3>
          <NavItem to="/" end>
            <FiHome />
            Tableau de bord
          </NavItem>
          <NavItem to="/transfer/new">
            <FiSend />
            Nouveau Transfert
          </NavItem>
          <NavItem to="/transfers">
            <FiList />
            Historique
          </NavItem>
        </NavSection>

        <NavSection>
          <h3>Gestion</h3>
          <NavItem to="/accounts">
            <FiCreditCard />
            Comptes
          </NavItem>
          <NavItem to="/kyc">
            <FiShield />
            KYC & Compliance
          </NavItem>
          <NavItem to="/analytics">
            <FiTrendingUp />
            Analytics
          </NavItem>
        </NavSection>

        <NavSection>
          <h3>Administration</h3>
          <NavItem to="/admin">
            <FiSettings />
            Administration
          </NavItem>
          <NavItem to="/users">
            <FiUsers />
            Utilisateurs
          </NavItem>
        </NavSection>
      </Nav>

      <Footer>
        <p>Version 1.0.0</p>
        <p>© 2024 Banking Transfer</p>
      </Footer>
    </SidebarContainer>
  );
};

export default Sidebar;