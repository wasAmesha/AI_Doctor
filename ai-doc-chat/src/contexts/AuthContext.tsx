'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, AuthContextType } from '@/types';
import { authAPI } from '@/lib/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (typeof window === 'undefined') return;
      
      const token = localStorage.getItem('token');
      if (token) {
        await fetchUserData();
      } else {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const fetchUserData = async () => {
    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await authAPI.login(email, password);
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', response.token);
      }
      setUser(response.user);
      return response;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const signup = async (email: string, password: string, name: string) => {
    try {
      const response = await authAPI.signup(email, password, name);
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', response.token);
      }
      setUser(response.user);
      return response;
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  };

  const logout = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};