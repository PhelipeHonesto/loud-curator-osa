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
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
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
  const [user, setUser] = useState<User | null>({ username: 'dev_user' });
  const [isLoading, setIsLoading] = useState<boolean>(false); // Was true, changed to false
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
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
    */
  }, []);

  const login = async (_username: string, _password: string) => {
    // This is a no-op since login is disabled.
    console.log('Login functionality is currently disabled.');
    setError(null);
    setIsLoading(true);
    // Simulate a successful login for UI consistency
    setIsAuthenticated(true);
    setUser({ username: 'dev_user' });
    navigate('/');
    setIsLoading(false);
  };

  const register = async (_username: string, _password: string) => {
    // This is a no-op since login is disabled.
    console.log('Register functionality is currently disabled.');
    setError(null);
    setIsLoading(true);
    // Simulate a successful registration for UI consistency
    setIsAuthenticated(true);
    setUser({ username: 'dev_user' });
    navigate('/');
    setIsLoading(false);
  };

  const logout = () => {
    // Also a no-op, but we'll clear state for completeness.
    setIsAuthenticated(false);
    setUser(null);
    localStorage.removeItem('token'); // Clear token just in case
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, register, logout, isLoading, error }}>
      {children}
    </AuthContext.Provider>
  );
}; 