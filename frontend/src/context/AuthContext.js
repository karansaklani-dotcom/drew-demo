import React, { createContext, useContext, useState, useEffect } from 'react';
import { mockUser } from '../mock/mockData';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on mount
    const storedUser = localStorage.getItem('drew_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const sendMagicLink = async (email) => {
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true });
      }, 2000);
    });
  };

  const signInWithGoogle = async () => {
    // Simulate OAuth flow
    return new Promise((resolve) => {
      setTimeout(() => {
        const newUser = {
          ...mockUser,
          email: 'google-user@example.com',
          hasCompletedOnboarding: false
        };
        setUser(newUser);
        localStorage.setItem('drew_user', JSON.stringify(newUser));
        resolve({ success: true, user: newUser });
      }, 2000);
    });
  };

  const completeOnboarding = (userData) => {
    const updatedUser = {
      ...user,
      ...userData,
      hasCompletedOnboarding: true
    };
    setUser(updatedUser);
    localStorage.setItem('drew_user', JSON.stringify(updatedUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('drew_user');
  };

  const value = {
    user,
    loading,
    sendMagicLink,
    signInWithGoogle,
    completeOnboarding,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
