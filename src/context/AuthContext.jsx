import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authTokens, setAuthTokens] = useState(() => {
    const storedTokens = localStorage.getItem('authTokens');
    return storedTokens ? JSON.parse(storedTokens) : null;
  });

  const login = async (username, password) => {
    try {
      const response = await fetch('/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (response.ok) {
        setAuthTokens(data);
        localStorage.setItem('authTokens', JSON.stringify(data));
      } else {
        throw new Error(data.detail || 'Login failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setAuthTokens(null);
    localStorage.removeItem('authTokens');
  };

  const refreshToken = async () => {
    try {
      const response = await fetch('/api/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: authTokens?.refresh }),
      });
      const data = await response.json();
      if (response.ok) {
        setAuthTokens((prevTokens) => ({ ...prevTokens, access: data.access }));
        localStorage.setItem('authTokens', JSON.stringify({ ...authTokens, access: data.access }));
      } else {
        throw new Error(data.detail || 'Token refresh failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const isAuthenticated = () => {
    return !!authTokens?.access;
  };

  return (
    <AuthContext.Provider value={{ authTokens, login, logout, refreshToken, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
