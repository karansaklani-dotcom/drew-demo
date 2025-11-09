import React, { useState } from "react";
import {
    Plug,
    CheckCircle,
    ExternalLink,
    Settings,
} from "lucide-react";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Switch } from "../ui/switch";
import { useToast } from "../../hooks/use-toast";

const Integrations = () => {
    const { toast } = useToast();
    const [integrations, setIntegrations] = useState([
        {
            id: 1,
            name: "Slack",
            description: "Get notifications and updates in your Slack workspace",
            icon: "💬",
            status: "connected",
            enabled: true,
        },
        {
            id: 2,
            name: "Google Calendar",
            description: "Sync events with your Google Calendar",
            icon: "📅",
            status: "connected",
            enabled: true,
        },
        {
            id: 3,
            name: "Stripe",
            description: "Process payments and manage subscriptions",
            icon: "💳",
            status: "connected",
            enabled: false,
        },
        {
            id: 4,
            name: "Mailchimp",
            description: "Send email campaigns and manage subscribers",
            icon: "✉️",
            status: "not_connected",
            enabled: false,
        },
        {
            id: 5,
            name: "Zoom",
            description: "Host virtual events and meetings",
            icon: "🎥",
            status: "not_connected",
            enabled: false,
        },
        {
            id: 6,
            name: "Salesforce",
            description: "Sync customer data with your CRM",
            icon: "☁️",
            status: "not_connected",
            enabled: false,
        },
    ]);

    const handleToggle = (id) => {
        setIntegrations(
            integrations.map((integration) =>
                integration.id === id
                    ? { ...integration, enabled: !integration.enabled }
                    : integration
            )
        );
        const integration = integrations.find((i) => i.id === id);
        toast({
            title: `${integration.name} ${!integration.enabled ? "enabled" : "disabled"}`,
            description: `Integration has been ${!integration.enabled ? "enabled" : "disabled"} successfully.`,
        });
    };

    const handleConnect = (name) => {
        toast({
            title: "Connecting...",
            description: `Redirecting to ${name} authentication...`,
        });
    };

    const handleDisconnect = (name) => {
        toast({
            title: "Disconnected",
            description: `${name} has been disconnected from your organization.`,
        });
    };

    const connectedCount = integrations.filter(
        (i) => i.status === "connected"
    ).length;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-gray-900">
                        Integrations
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Connect third-party services to enhance your workflow
                    </p>
                </div>
                <div className="text-right">
                    <p className="text-sm text-gray-600">
                        Connected Integrations
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                        {connectedCount}/{integrations.length}
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-green-900">
                                Active
                            </p>
                            <p className="text-2xl font-bold text-green-900 mt-1">
                                {integrations.filter((i) => i.enabled).length}
                            </p>
                        </div>
                        <CheckCircle className="h-8 w-8 text-green-600" />
                    </div>
                </div>
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-blue-900">
                                Connected
                            </p>
                            <p className="text-2xl font-bold text-blue-900 mt-1">
                                {connectedCount}
                            </p>
                        </div>
                        <Plug className="h-8 w-8 text-blue-600" />
                    </div>
                </div>
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-4 border border-gray-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-900">
                                Available
                            </p>
                            <p className="text-2xl font-bold text-gray-900 mt-1">
                                {integrations.length}
                            </p>
                        </div>
                        <Settings className="h-8 w-8 text-gray-600" />
                    </div>
                </div>
            </div>

            <div className="space-y-4">
                {integrations.map((integration) => (
                    <div
                        key={integration.id}
                        className="border rounded-lg p-6 hover:shadow-md transition-shadow"
                    >
                        <div className="flex items-start justify-between">
                            <div className="flex items-start gap-4 flex-1">
                                <div className="text-4xl">{integration.icon}</div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-3">
                                        <h3 className="text-lg font-semibold text-gray-900">
                                            {integration.name}
                                        </h3>
                                        {integration.status === "connected" ? (
                                            <Badge className="bg-green-100 text-green-800">
                                                <CheckCircle className="mr-1 h-3 w-3" />
                                                Connected
                                            </Badge>
                                        ) : (
                                            <Badge className="bg-gray-100 text-gray-800">
                                                Not Connected
                                            </Badge>
                                        )}
                                    </div>
                                    <p className="text-sm text-gray-600 mt-1">
                                        {integration.description}
                                    </p>
                                    {integration.status === "connected" && (
                                        <div className="flex items-center gap-2 mt-3">
                                            <Switch
                                                checked={integration.enabled}
                                                onCheckedChange={() =>
                                                    handleToggle(integration.id)
                                                }
                                            />
                                            <span className="text-sm text-gray-600">
                                                {integration.enabled
                                                    ? "Enabled"
                                                    : "Disabled"}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div className="flex gap-2">
                                {integration.status === "connected" ? (
                                    <>
                                        <Button variant="outline" size="sm">
                                            <Settings className="mr-2 h-4 w-4" />
                                            Configure
                                        </Button>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() =>
                                                handleDisconnect(integration.name)
                                            }
                                        >
                                            Disconnect
                                        </Button>
                                    </>
                                ) : (
                                    <Button
                                        size="sm"
                                        onClick={() =>
                                            handleConnect(integration.name)
                                        }
                                    >
                                        <ExternalLink className="mr-2 h-4 w-4" />
                                        Connect
                                    </Button>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Integrations;
