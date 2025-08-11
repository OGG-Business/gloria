import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      setIsAuthenticated(true);
      fetchUserData();
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserData = async () => {
    try {
      // Mock user data for now
      const userData = {
        id: "1",
        username: "demo",
        email: "demo@example.com",
        firstName: "Demo",
        lastName: "User",
        roles: ["USER"],
        permissions: ["READ"],
        kycStatus: "APPROVED",
        amlStatus: "CLEAR",
        riskLevel: "LOW",
        mfaEnabled: false,
        isActive: true
      };
      setUser(userData);
    } catch (error) {
      console.error("Failed to fetch user data:", error);
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials) => {
    // Mock login for now
    localStorage.setItem("accessToken", "mock-token");
    localStorage.setItem("refreshToken", "mock-refresh-token");
    setIsAuthenticated(true);
    await fetchUserData();
  };

  const logout = async () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    setIsAuthenticated(false);
    setUser(null);
  };

  const refreshToken = async () => {
    // Mock refresh for now
    localStorage.setItem("accessToken", "new-mock-token");
    setIsAuthenticated(true);
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
