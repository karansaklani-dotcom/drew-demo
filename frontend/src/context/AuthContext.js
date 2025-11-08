import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
    const token = localStorage.getItem('drew_token');
    if (token) {
      fetchCurrentUser(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async (token) => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      localStorage.removeItem('drew_token');
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        username,
        email,
        password
      });
      
      const { token, user: userData } = response.data;
      localStorage.setItem('drew_token', token);
      setUser(userData);
      
      return { success: true, user: userData };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password
      });
      
      const { token, user: userData } = response.data;
      localStorage.setItem('drew_token', token);
      setUser(userData);
      
      return { success: true, user: userData };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const sendMagicLink = async (email) => {
    try {
      await axios.post(`${API}/auth/magic-link`, { email });
      return { success: true };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send magic link');
    }
  };

  const signInWithGoogle = async () => {
    // This will be implemented when Google OAuth credentials are provided
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockUser = {
          id: 'google-user',
          email: 'google-user@example.com',
          username: 'googleuser',
          hasCompletedOnboarding: false
        };
        setUser(mockUser);
        localStorage.setItem('drew_token', 'mock-google-token');
        resolve({ success: true, user: mockUser });
      }, 1000);
    });
  };

  const completeOnboarding = async (userData) => {
    try {
      const token = localStorage.getItem('drew_token');
      const response = await axios.post(`${API}/users/onboarding`, userData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const updatedUser = response.data.user;
      setUser(updatedUser);
      
      return { success: true, user: updatedUser };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to complete onboarding');
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('drew_token');
  };

  const value = {
    user,
    loading,
    register,
    login,
    sendMagicLink,
    signInWithGoogle,
    completeOnboarding,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
