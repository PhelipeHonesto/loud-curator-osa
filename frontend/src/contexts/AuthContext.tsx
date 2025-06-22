import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { getCurrentUser } from '../services/api';
import * as api from '../services/api';
import { useNavigate } from 'react-router-dom';

interface User {
  username: string;
  email?: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: any;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  // LOGIN DISABLED: Defaulting to an authenticated state for development.
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(true);
  const [user, setUser] = useState<any>({ username: 'dev_user' });
  const [loading, setLoading] = useState<boolean>(false); // Was true, changed to false
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Since login is disabled, this check is bypassed.
    // If you re-enable login, uncomment this.
    /*
    const token = localStorage.getItem('token');
    if (token) {
      api.getCurrentUser()
        .then(userData => {
          setUser(userData);
          setIsAuthenticated(true);
        })
        .catch(() => {
          localStorage.removeItem('token');
          setIsAuthenticated(false);
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
    */
  }, []);

  const login = async (username: string, password: string) => {
    // This is a no-op since login is disabled.
    console.log('Login functionality is currently disabled.');
    setError(null);
    setLoading(true);
    // Simulate a successful login for UI consistency
    setIsAuthenticated(true);
    setUser({ username: 'dev_user' });
    navigate('/');
    setLoading(false);
  };

  const register = async (username: string, password: string) => {
    // This is a no-op since login is disabled.
    console.log('Register functionality is currently disabled.');
    setError(null);
    setLoading(true);
    // Simulate a successful registration for UI consistency
    setIsAuthenticated(true);
    setUser({ username: 'dev_user' });
    navigate('/');
    setLoading(false);
  };

  const logout = () => {
    // Also a no-op, but we'll clear state for completeness.
    setIsAuthenticated(false);
    setUser(null);
    localStorage.removeItem('token'); // Clear token just in case
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, register, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
}; 