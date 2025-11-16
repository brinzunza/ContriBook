import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../lib/api';
import type { User, LoginCredentials, RegisterData } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (token) {
      // Add timeout to prevent infinite loading
      const timeoutId = setTimeout(() => {
        setLoading(false);
        console.error('Auth check timed out');
      }, 5000); // 5 second timeout

      authApi
        .getCurrentUser()
        .then((res) => {
          clearTimeout(timeoutId);
          setUser(res.data);
          setLoading(false);
        })
        .catch((error) => {
          clearTimeout(timeoutId);
          console.error('Auth check failed:', error);
          localStorage.removeItem('token');
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials);
      localStorage.setItem('token', response.data.access_token);

      const userResponse = await authApi.getCurrentUser();
      setUser(userResponse.data);
    } catch (error) {
      // Remove token if login fails
      localStorage.removeItem('token');
      throw error; // Re-throw to let the Login component handle it
    }
  };

  const register = async (data: RegisterData) => {
    await authApi.register(data);
    // Auto-login after registration
    await login({ username: data.username, password: data.password });
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
