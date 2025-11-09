import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useOrganization } from "../hooks/use-organization";
import { isProfileComplete } from "../utils/onboarding";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "../components/ui/card";
import { Separator } from "../components/ui/separator";
import { Badge } from "../components/ui/badge";
import { toast } from "../hooks/use-toast";
import {
    ArrowLeft,
    User,
    Mail,
    Building,
    Briefcase,
    Globe,
    LogOut,
    Loader2,
} from "lucide-react";

const Profile = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);

    // Fetch organization data if user has organizationId
    const { data: organization, isLoading: orgLoading } = useOrganization(
        user?.organizationId
    );

    if (!user) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="h-12 w-12 animate-spin text-purple-600" />
            </div>
        );
    }

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
            {/* Header */}
            <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <Button
                            variant="ghost"
                            onClick={() => navigate("/")}
                            className="gap-2"
                        >
                            <ArrowLeft className="h-4 w-4" />
                            Back to Events
                        </Button>
                        <img
                            src="/assets/logo-small.png"
                            alt="Drew"
                            className="h-8"
                        />
                        <div className="w-24"></div>
                    </div>
                </div>
            </header>

            {/* Content */}
            <div className="max-w-4xl mx-auto px-4 py-12">
                <div className="mb-8">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h1 className="text-4xl font-bold mb-2">Profile</h1>
                            <p className="text-gray-600">
                                Manage your account information
                            </p>
                        </div>
                        {organization && (
                            <Badge
                                variant="secondary"
                                className="flex items-center gap-2 px-4 py-2 text-base h-auto rounded-lg"
                            >
                                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-purple-100 text-purple-600">
                                    <Building className="h-4 w-4" />
                                </div>
                                <span className="font-semibold">
                                    {organization.name}
                                </span>
                            </Badge>
                        )}
                    </div>
                </div>

                <div className="grid gap-6">
                    {/* Personal Information */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Personal Information</CardTitle>
                            <CardDescription>
                                Your basic account details
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <Label className="text-sm font-medium text-gray-700">
                                        Email
                                    </Label>
                                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                                        <Mail className="h-5 w-5 text-gray-500" />
                                        <span className="text-gray-900">
                                            {user.email}
                                        </span>
                                    </div>
                                </div>

                                {user.firstName && (
                                    <div className="space-y-2">
                                        <Label className="text-sm font-medium text-gray-700">
                                            First Name
                                        </Label>
                                        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                                            <User className="h-5 w-5 text-gray-500" />
                                            <span className="text-gray-900">
                                                {user.firstName}
                                            </span>
                                        </div>
                                    </div>
                                )}

                                {user.lastName && (
                                    <div className="space-y-2">
                                        <Label className="text-sm font-medium text-gray-700">
                                            Last Name
                                        </Label>
                                        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                                            <User className="h-5 w-5 text-gray-500" />
                                            <span className="text-gray-900">
                                                {user.lastName}
                                            </span>
                                        </div>
                                    </div>
                                )}

                                {user.role && (
                                    <div className="space-y-2">
                                        <Label className="text-sm font-medium text-gray-700">
                                            Role
                                        </Label>
                                        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                                            <Briefcase className="h-5 w-5 text-gray-500" />
                                            <span className="text-gray-900 capitalize">
                                                {user.role}
                                            </span>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {!isProfileComplete(user) && (
                                <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                                    <p className="text-sm text-yellow-800 mb-2">
                                        Complete your profile to get the most
                                        out of Drew!
                                    </p>
                                    <Button
                                        onClick={() => navigate("/onboarding")}
                                        variant="outline"
                                        className="mt-2"
                                    >
                                        Complete Onboarding
                                    </Button>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Account Status */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Account Status</CardTitle>
                            <CardDescription>
                                Your account information and status
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                <div>
                                    <p className="font-medium text-gray-900">
                                        Onboarding Status
                                    </p>
                                    <p className="text-sm text-gray-600 mt-1">
                                        {isProfileComplete(user)
                                            ? "Completed"
                                            : "Incomplete"}
                                    </p>
                                </div>
                                <div
                                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                                        isProfileComplete(user)
                                            ? "bg-green-100 text-green-800"
                                            : "bg-yellow-100 text-yellow-800"
                                    }`}
                                >
                                    {isProfileComplete(user)
                                        ? "✓ Complete"
                                        : "○ Pending"}
                                </div>
                            </div>

                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                <div>
                                    <p className="font-medium text-gray-900">
                                        Account Created
                                    </p>
                                    <p className="text-sm text-gray-600 mt-1">
                                        {user.createdAt
                                            ? new Date(
                                                  user.createdAt
                                              ).toLocaleDateString("en-US", {
                                                  year: "numeric",
                                                  month: "long",
                                                  day: "numeric",
                                              })
                                            : "Recently"}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Actions */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Account Actions</CardTitle>
                            <CardDescription>
                                Manage your account
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Button
                                onClick={handleLogout}
                                variant="destructive"
                                className="w-full md:w-auto"
                            >
                                <LogOut className="mr-2 h-4 w-4" />
                                Logout
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default Profile;
