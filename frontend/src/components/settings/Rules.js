import React, { useState } from "react";
import { Shield, Plus, Trash2, Edit } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../ui/select";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "../ui/dialog";
import { Badge } from "../ui/badge";
import { Switch } from "../ui/switch";
import { useToast } from "../../hooks/use-toast";

const Rules = () => {
    const { toast } = useToast();
    const [rules, setRules] = useState([
        {
            id: 1,
            name: "Event Approval Required",
            description:
                "All events must be approved by a manager before being published",
            type: "Approval",
            enabled: true,
        },
        {
            id: 2,
            name: "Budget Threshold Alert",
            description:
                "Send notification when expense exceeds 80% of category budget",
            type: "Budget",
            enabled: true,
        },
        {
            id: 3,
            name: "User Invitation Limit",
            description: "Admins can invite maximum 50 users per month",
            type: "Access",
            enabled: true,
        },
        {
            id: 4,
            name: "Auto-Archive Events",
            description:
                "Automatically archive events 30 days after they conclude",
            type: "Automation",
            enabled: false,
        },
        {
            id: 5,
            name: "Mandatory Event Categories",
            description: "All events must have at least one category assigned",
            type: "Validation",
            enabled: true,
        },
    ]);

    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
    const [newRule, setNewRule] = useState({
        name: "",
        description: "",
        type: "Approval",
    });

    const handleToggleRule = (id) => {
        setRules(
            rules.map((rule) =>
                rule.id === id ? { ...rule, enabled: !rule.enabled } : rule
            )
        );
        const rule = rules.find((r) => r.id === id);
        toast({
            title: `Rule ${!rule.enabled ? "enabled" : "disabled"}`,
            description: `${rule.name} has been ${!rule.enabled ? "enabled" : "disabled"}.`,
        });
    };

    const handleAddRule = () => {
        const rule = {
            id: rules.length + 1,
            ...newRule,
            enabled: true,
        };
        setRules([...rules, rule]);
        setNewRule({ name: "", description: "", type: "Approval" });
        setIsAddDialogOpen(false);
        toast({
            title: "Rule added",
            description: "New rule has been added successfully.",
        });
    };

    const handleDeleteRule = (id) => {
        setRules(rules.filter((rule) => rule.id !== id));
        toast({
            title: "Rule deleted",
            description: "Rule has been removed from your organization.",
        });
    };

    const getRuleTypeColor = (type) => {
        switch (type) {
            case "Approval":
                return "bg-blue-100 text-blue-800";
            case "Budget":
                return "bg-green-100 text-green-800";
            case "Access":
                return "bg-purple-100 text-purple-800";
            case "Automation":
                return "bg-orange-100 text-orange-800";
            case "Validation":
                return "bg-pink-100 text-pink-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    };

    const ruleTypes = ["Approval", "Budget", "Access", "Automation", "Validation"];
    const activeRules = rules.filter((r) => r.enabled).length;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-gray-900">Rules</h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Define and manage organizational rules and policies
                    </p>
                </div>
                <Dialog
                    open={isAddDialogOpen}
                    onOpenChange={setIsAddDialogOpen}
                >
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            Add Rule
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Create New Rule</DialogTitle>
                            <DialogDescription>
                                Add a new rule to enforce organizational policies
                            </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 py-4">
                            <div className="space-y-2">
                                <Label htmlFor="ruleName">Rule Name</Label>
                                <Input
                                    id="ruleName"
                                    value={newRule.name}
                                    onChange={(e) =>
                                        setNewRule({
                                            ...newRule,
                                            name: e.target.value,
                                        })
                                    }
                                    placeholder="Enter rule name"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="ruleDescription">
                                    Description
                                </Label>
                                <Textarea
                                    id="ruleDescription"
                                    value={newRule.description}
                                    onChange={(e) =>
                                        setNewRule({
                                            ...newRule,
                                            description: e.target.value,
                                        })
                                    }
                                    placeholder="Describe what this rule does"
                                    rows={3}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="ruleType">Rule Type</Label>
                                <Select
                                    value={newRule.type}
                                    onValueChange={(value) =>
                                        setNewRule({ ...newRule, type: value })
                                    }
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {ruleTypes.map((type) => (
                                            <SelectItem key={type} value={type}>
                                                {type}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                        <DialogFooter>
                            <Button
                                variant="outline"
                                onClick={() => setIsAddDialogOpen(false)}
                            >
                                Cancel
                            </Button>
                            <Button onClick={handleAddRule}>Create Rule</Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-blue-900">
                                Total Rules
                            </p>
                            <p className="text-3xl font-bold text-blue-900 mt-2">
                                {rules.length}
                            </p>
                        </div>
                        <Shield className="h-10 w-10 text-blue-600" />
                    </div>
                    <p className="text-xs text-blue-700 mt-2">
                        Organizational policies
                    </p>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-green-900">
                                Active Rules
                            </p>
                            <p className="text-3xl font-bold text-green-900 mt-2">
                                {activeRules}
                            </p>
                        </div>
                        <Shield className="h-10 w-10 text-green-600" />
                    </div>
                    <p className="text-xs text-green-700 mt-2">
                        Currently enforced
                    </p>
                </div>
            </div>

            <div className="space-y-3">
                {rules.map((rule) => (
                    <div
                        key={rule.id}
                        className="border rounded-lg p-5 hover:shadow-md transition-shadow"
                    >
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                    <h3 className="text-lg font-semibold text-gray-900">
                                        {rule.name}
                                    </h3>
                                    <Badge className={getRuleTypeColor(rule.type)}>
                                        {rule.type}
                                    </Badge>
                                    {rule.enabled ? (
                                        <Badge className="bg-green-100 text-green-800">
                                            Active
                                        </Badge>
                                    ) : (
                                        <Badge className="bg-gray-100 text-gray-800">
                                            Inactive
                                        </Badge>
                                    )}
                                </div>
                                <p className="text-sm text-gray-600">
                                    {rule.description}
                                </p>
                            </div>
                            <div className="flex items-center gap-3 ml-4">
                                <Switch
                                    checked={rule.enabled}
                                    onCheckedChange={() => handleToggleRule(rule.id)}
                                />
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8"
                                >
                                    <Edit className="h-4 w-4" />
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                                    onClick={() => handleDeleteRule(rule.id)}
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Rules;
