import React, { useState } from 'react';
import styled from 'styled-components';
import { FiBell, FiUser, FiSettings, FiLogOut, FiSearch } from 'react-icons/fi';
import { useAuth } from '../hooks/useAuth';

const HeaderContainer = styled.header`
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  flex: 1;
  max-width: 400px;
  margin: 0 2rem;

  input {
    border: none;
    background: transparent;
    outline: none;
    width: 100%;
    margin-left: 0.5rem;
    font-size: 0.9rem;

    &::placeholder {
      color: #a0aec0;
    }
  }
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const NotificationButton = styled.button`
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  color: #4a5568;
  transition: all 0.2s;

  &:hover {
    background: #f7fafc;
    color: #2d3748;
  }
`;

const NotificationBadge = styled.span`
  position: absolute;
  top: 0;
  right: 0;
  background: #e53e3e;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const UserMenu = styled.div`
  position: relative;
`;

const UserButton = styled.button`
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4a5568;
  transition: all 0.2s;

  &:hover {
    background: #f7fafc;
    color: #2d3748;
  }
`;

const DropdownMenu = styled.div<{ isOpen: boolean }>`
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  min-width: 200px;
  z-index: 1000;
  opacity: ${props => props.isOpen ? 1 : 0};
  visibility: ${props => props.isOpen ? 'visible' : 'hidden'};
  transform: ${props => props.isOpen ? 'translateY(0)' : 'translateY(-10px)'};
  transition: all 0.2s;
`;

const MenuItem = styled.button`
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4a5568;
  transition: all 0.2s;

  &:hover {
    background: #f7fafc;
    color: #2d3748;
  }

  &:first-child {
    border-radius: 8px 8px 0 0;
  }

  &:last-child {
    border-radius: 0 0 8px 8px;
    border-top: 1px solid #e2e8f0;
  }
`;

const Header: React.FC = () => {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    setIsUserMenuOpen(false);
  };

  return (
    <HeaderContainer>
      <SearchBar>
        <FiSearch size={16} color="#a0aec0" />
        <input
          type="text"
          placeholder="Rechercher des transferts, comptes..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </SearchBar>

      <RightSection>
        <NotificationButton>
          <FiBell size={20} />
          <NotificationBadge>3</NotificationBadge>
        </NotificationButton>

        <UserMenu>
          <UserButton onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}>
            <FiUser size={20} />
            <span>{user?.name || 'Utilisateur'}</span>
          </UserButton>

          <DropdownMenu isOpen={isUserMenuOpen}>
            <MenuItem onClick={() => setIsUserMenuOpen(false)}>
              <FiUser size={16} />
              Profil
            </MenuItem>
            <MenuItem onClick={() => setIsUserMenuOpen(false)}>
              <FiSettings size={16} />
              Paramètres
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <FiLogOut size={16} />
              Déconnexion
            </MenuItem>
          </DropdownMenu>
        </UserMenu>
      </RightSection>
    </HeaderContainer>
  );
};

export default Header;