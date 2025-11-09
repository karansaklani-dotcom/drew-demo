import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    Building,
    Users,
    Plug,
    DollarSign,
    Shield,
    ArrowLeft,
    Settings,
    User,
    Globe,
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
import BudgetAndCosting from "../components/settings/BudgetAndCosting";
import Rules from "../components/settings/Rules";

const OrganizationSettings = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState("basic");

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
            id: "integrations",
            label: "Integrations",
            icon: Plug,
            component: Integrations,
        },
        {
            id: "budget",
            label: "Budget and Costing",
            icon: DollarSign,
            component: BudgetAndCosting,
        },
        {
            id: "rules",
            label: "Rules",
            icon: Shield,
            component: Rules,
        },
    ];

    const ActiveComponent =
        tabs.find((tab) => tab.id === activeTab)?.component || BasicDetails;

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
                                <ArrowLeft className="h-5 w-5" />
                            </Button>
                            <img
                                src="/assets/logo-small.png"
                                alt="Drew"
                                className="h-8"
                            />
                        </div>

                        {/* Title */}
                        <div className="flex-1 text-center">
                            <h1 className="text-xl font-semibold">
                                Organization Settings
                            </h1>
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
                    {/* Sidebar */}
                    <aside className="w-64 flex-shrink-0">
                        <nav className="space-y-1 bg-white rounded-lg shadow-sm p-2">
                            {tabs.map((tab) => {
                                const Icon = tab.icon;
                                const isActive = activeTab === tab.id;
                                return (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                                            isActive
                                                ? "bg-gray-100 text-gray-900 font-medium"
                                                : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                        }`}
                                    >
                                        <Icon className="h-5 w-5" />
                                        <span>{tab.label}</span>
                                    </button>
                                );
                            })}
                        </nav>
                    </aside>

                    {/* Content Area */}
                    <main className="flex-1 bg-white rounded-lg shadow-sm p-8">
                        <ActiveComponent />
                    </main>
                </div>
            </div>
        </div>
    );
};

export default OrganizationSettings;
