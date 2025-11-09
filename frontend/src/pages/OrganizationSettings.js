import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useOrganization } from "../hooks/use-organization";
import {
    Building,
    Users,
    Plug,
    Settings,
    User,
    Globe,
    MapPin,
} from "lucide-react";
import { Button } from "../components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "../components/ui/dropdown-menu";
import BasicDetails from "../components/settings/BasicDetails";
import UsersAndRoles from "../components/settings/UsersAndRoles";
import Integrations from "../components/settings/Integrations";
import Offices from "../components/settings/Offices";
import { Loader2 } from "lucide-react";

const OrganizationSettings = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState("basic");

    // Fetch organization data
    const { data: organization, isLoading: orgLoading } = useOrganization(
        user?.organizationId
    );

    const tabs = [
        {
            id: "basic",
            label: "Basic Details",
            icon: Building,
            component: BasicDetails,
        },
        {
            id: "users",
            label: "Users and Roles",
            icon: Users,
            component: UsersAndRoles,
        },
        {
            id: "offices",
            label: "Offices",
            icon: MapPin,
            component: Offices,
        },
        {
            id: "integrations",
            label: "Integrations",
            icon: Plug,
            component: Integrations,
        },
    ];

    const ActiveComponent =
        tabs.find((tab) => tab.id === activeTab)?.component || BasicDetails;

    if (orgLoading || !organization) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-white">
                <Loader2 className="h-12 w-12 animate-spin text-gray-600" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Top Navigation */}
            <header className="border-b sticky top-0 bg-white z-50">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        {/* Logo */}
                        <div className="flex items-center gap-4">
                            <Button
                                variant="ghost"
                                size="icon"
                                className="rounded-full"
                                onClick={() => navigate("/")}
                            >
                                <img
                                    src="/assets/logo-small.png"
                                    alt="Drew"
                                    className="h-6"
                                />
                            </Button>
                        </div>

                        {/* Right icons */}
                        <div className="flex items-center gap-4">
                            <Button
                                variant="ghost"
                                size="icon"
                                className="rounded-full"
                            >
                                <Globe className="h-5 w-5" />
                            </Button>
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="rounded-full"
                                    >
                                        <Settings className="h-5 w-5" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                    <DropdownMenuItem
                                        onClick={() => navigate("/profile")}
                                    >
                                        <User className="mr-2 h-4 w-4" />
                                        Profile Settings
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                        onClick={() =>
                                            navigate("/settings/organization")
                                        }
                                    >
                                        <Building className="mr-2 h-4 w-4" />
                                        Organization Settings
                                    </DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="rounded-full bg-gray-100 hover:bg-gray-200"
                                onClick={() => navigate("/profile")}
                                title="Profile"
                            >
                                <User className="h-5 w-5" />
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="flex gap-8">
                    {/* Sticky Sidebar */}
                    <aside className="w-56 flex-shrink-0">
                        <nav className="sticky top-20 space-y-1 bg-white border border-gray-200 rounded-lg p-2">
                            {tabs.map((tab) => {
                                const Icon = tab.icon;
                                const isActive = activeTab === tab.id;
                                return (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors ${
                                            isActive
                                                ? "bg-gray-100 text-gray-900 font-medium"
                                                : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                        }`}
                                    >
                                        <Icon className="h-3.5 w-3.5" />
                                        <span>{tab.label}</span>
                                    </button>
                                );
                            })}
                        </nav>
                    </aside>

                    {/* Content Area */}
                    <main className="flex-1 bg-white border border-gray-200 rounded-lg shadow-sm p-8">
                        <ActiveComponent organization={organization} />
                    </main>
                </div>
            </div>
        </div>
    );
};

export default OrganizationSettings;
