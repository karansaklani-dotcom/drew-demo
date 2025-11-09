import React, { createContext, useContext } from "react";
import { useUserMe, useUserRegister, useUserVerify } from "../hooks/use-user";
import { useOnboardingComplete } from "../hooks/use-onboarding";
import { api, clearAuthToken, getAuthToken } from "../utils/api";
import { useQueryClient } from "@tanstack/react-query";
import { endpoints } from "../utils/endpoints";

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within AuthProvider");
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    // Use the useUserMe hook to get current user
    const { data: user, isLoading: loading, error } = useUserMe();
    const registerMutation = useUserRegister();
    const verifyMutation = useUserVerify();
    const onboardingMutation = useOnboardingComplete();
    const queryClient = useQueryClient();

    const register = async (email, password) => {
        try {
            const userData = await registerMutation.mutateAsync({
                email,
                password,
            });
            return { success: true, user: userData };
        } catch (error) {
            const message =
                error.response?.data?.message ||
                error.message ||
                "Registration failed";
            throw new Error(message);
        }
    };

    const login = async (email, password) => {
        try {
            const userData = await verifyMutation.mutateAsync({
                email,
                password,
            });
            return { success: true, user: userData };
        } catch (error) {
            const message =
                error.response?.data?.message ||
                error.message ||
                "Login failed";
            throw new Error(message);
        }
    };

    const sendMagicLink = async (email) => {
        try {
            // Magic link endpoint - to be implemented in drew-ai
            await api("auth/magic-link", {
                method: "POST",
                data: { email },
            });
            return { success: true };
        } catch (error) {
            const message =
                error.response?.data?.message ||
                error.message ||
                "Failed to send magic link";
            throw new Error(message);
        }
    };

    const signInWithGoogle = async () => {
        try {
            // Google OAuth endpoint - to be implemented in drew-ai
            // For now, redirect to OAuth flow
            window.location.href = `${
                process.env.REACT_APP_DREW_AI_BACKEND_URL ||
                "http://localhost:3000"
            }/auth/google/redirect`;
            return { success: true };
        } catch (error) {
            const message =
                error.response?.data?.message ||
                error.message ||
                "Failed to sign in with Google";
            throw new Error(message);
        }
    };

    const completeOnboarding = async (userData) => {
        try {
            await onboardingMutation.mutate(userData);
            // The hook will invalidate queries and update the cache
            return { success: true };
        } catch (error) {
            const message =
                error.response?.data?.message ||
                error.message ||
                "Failed to complete onboarding";
            throw new Error(message);
        }
    };

    const logout = async () => {
        try {
            // Call logout endpoint if available
            await api("auth/logout", { method: "POST" });
        } catch (error) {
            console.error("Logout error:", error);
        } finally {
            // Clear the user from cache
            queryClient.setQueryData(endpoints.user.me.getKeys(), null);
        }
    };

    const value = {
        user: user || null,
        loading,
        setUser: (newUser) => {
            // Update the cache when setUser is called
            queryClient.setQueryData(endpoints.user.me.getKeys(), newUser);
        },
        register,
        login,
        sendMagicLink,
        signInWithGoogle,
        completeOnboarding,
        logout,
    };

    return (
        <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );
};
