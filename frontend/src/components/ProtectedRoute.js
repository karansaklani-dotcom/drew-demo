import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { isProfileComplete } from "../utils/onboarding";

export const ProtectedRoute = ({
    children,
    allowWithoutOrganization = false,
}) => {
    const { user, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    // If allowWithoutOrganization is true (e.g., for onboarding route), allow access
    if (allowWithoutOrganization) {
        return children;
    }

    // Check if profile is complete
    const profileComplete = isProfileComplete(user);

    // Redirect to onboarding if profile is incomplete
    // Only redirect if not already on onboarding page
    if (!profileComplete && location.pathname !== "/onboarding") {
        return <Navigate to="/onboarding" replace />;
    }

    return children;
};

export const PublicRoute = ({ children }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            </div>
        );
    }

    // If user is logged in, check if profile is complete
    if (user) {
        const profileComplete = isProfileComplete(user);

        // If profile is complete, redirect to home
        if (profileComplete) {
            return <Navigate to="/" replace />;
        }

        // If profile is incomplete, redirect to onboarding
        if (!profileComplete) {
            return <Navigate to="/onboarding" replace />;
        }
    }

    return children;
};
