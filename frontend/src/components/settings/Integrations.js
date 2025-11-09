import React, { useState } from "react";
import { Settings, Plug2, X } from "lucide-react";
import { Button } from "../ui/button";
import { useToast } from "../../hooks/use-toast";

const Integrations = () => {
    const { toast } = useToast();
    const [integrations, setIntegrations] = useState([
        {
            id: 1,
            name: "Slack",
            logo: "💬",
            status: "connected",
        },
        {
            id: 2,
            name: "Google Calendar",
            logo: "📅",
            status: "connected",
        },
        {
            id: 3,
            name: "Stripe",
            logo: "💳",
            status: "not_connected",
        },
        {
            id: 4,
            name: "Mailchimp",
            logo: "✉️",
            status: "not_connected",
        },
        {
            id: 5,
            name: "Zoom",
            logo: "🎥",
            status: "not_connected",
        },
        {
            id: 6,
            name: "Salesforce",
            logo: "☁️",
            status: "not_connected",
        },
    ]);

    const handleConnect = (name) => {
        toast({
            title: "Connecting...",
            description: `Redirecting to ${name} authentication...`,
        });
    };

    const handleDisconnect = (name) => {
        setIntegrations(
            integrations.map((integration) =>
                integration.name === name
                    ? { ...integration, status: "not_connected" }
                    : integration
            )
        );
        toast({
            title: "Disconnected",
            description: `${name} has been disconnected from your organization.`,
        });
    };

    const handleConfigure = (name) => {
        toast({
            title: "Configure",
            description: `Opening ${name} configuration...`,
        });
    };

    return (
        <div className="space-y-6">
            <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900">
                    Integrations
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                    Connect third-party services to enhance your workflow
                </p>
            </div>

            <div className="space-y-3">
                {integrations.map((integration) => (
                    <div
                        key={integration.id}
                        className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
                    >
                        <div className="flex items-center gap-4">
                            <div className="text-3xl">{integration.logo}</div>
                            <div>
                                <p className="text-sm font-medium text-gray-900">
                                    {integration.name}
                                </p>
                                <p
                                    className={`text-xs mt-1 ${
                                        integration.status === "connected"
                                            ? "text-black font-medium"
                                            : "text-gray-500"
                                    }`}
                                >
                                    {integration.status === "connected"
                                        ? "Connected"
                                        : "Not connected"}
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            {integration.status === "connected" ? (
                                <>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() =>
                                            handleConfigure(integration.name)
                                        }
                                        className="border-gray-300"
                                    >
                                        <Settings className="mr-2 h-4 w-4" />
                                        Configure
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() =>
                                            handleDisconnect(integration.name)
                                        }
                                        className="border-gray-300"
                                    >
                                        <X className="mr-2 h-4 w-4" />
                                        Disconnect
                                    </Button>
                                </>
                            ) : (
                                <Button
                                    size="sm"
                                    onClick={() =>
                                        handleConnect(integration.name)
                                    }
                                    className="bg-black hover:bg-gray-800 text-white"
                                >
                                    <Plug2 className="mr-2 h-4 w-4" />
                                    Connect
                                </Button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Integrations;
