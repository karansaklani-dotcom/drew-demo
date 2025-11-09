import React, { useState } from "react";
import {
    DollarSign,
    TrendingUp,
    TrendingDown,
    Calendar,
    Save,
} from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../ui/select";
import { useToast } from "../../hooks/use-toast";

const BudgetAndCosting = () => {
    const { toast } = useToast();
    const [isEditing, setIsEditing] = useState(false);
    const [budgetData, setBudgetData] = useState({
        monthlyBudget: "10000",
        currency: "USD",
        fiscalYearStart: "January",
        approvalRequired: "500",
    });

    const expenses = [
        {
            category: "Events",
            budgeted: 5000,
            spent: 3200,
            percentage: 64,
            trend: "up",
        },
        {
            category: "Marketing",
            budgeted: 2000,
            spent: 1800,
            percentage: 90,
            trend: "up",
        },
        {
            category: "Software & Tools",
            budgeted: 1500,
            spent: 1500,
            percentage: 100,
            trend: "neutral",
        },
        {
            category: "Operations",
            budgeted: 1500,
            spent: 800,
            percentage: 53,
            trend: "down",
        },
    ];

    const totalBudgeted = expenses.reduce((sum, exp) => sum + exp.budgeted, 0);
    const totalSpent = expenses.reduce((sum, exp) => sum + exp.spent, 0);
    const percentageUsed = ((totalSpent / totalBudgeted) * 100).toFixed(1);

    const handleSave = () => {
        toast({
            title: "Budget settings saved",
            description: "Budget and costing settings have been updated.",
        });
        setIsEditing(false);
    };

    const handleChange = (field, value) => {
        setBudgetData((prev) => ({ ...prev, [field]: value }));
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-gray-900">
                        Budget and Costing
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Manage your organization's budget and track expenses
                    </p>
                </div>
                {!isEditing ? (
                    <Button onClick={() => setIsEditing(true)}>
                        Edit Settings
                    </Button>
                ) : (
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            onClick={() => setIsEditing(false)}
                        >
                            Cancel
                        </Button>
                        <Button onClick={handleSave}>
                            <Save className="mr-2 h-4 w-4" />
                            Save Changes
                        </Button>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-blue-900">
                                Total Budget
                            </p>
                            <p className="text-3xl font-bold text-blue-900 mt-2">
                                ${totalBudgeted.toLocaleString()}
                            </p>
                        </div>
                        <DollarSign className="h-10 w-10 text-blue-600" />
                    </div>
                    <p className="text-xs text-blue-700 mt-2">This month</p>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-green-900">
                                Total Spent
                            </p>
                            <p className="text-3xl font-bold text-green-900 mt-2">
                                ${totalSpent.toLocaleString()}
                            </p>
                        </div>
                        <TrendingUp className="h-10 w-10 text-green-600" />
                    </div>
                    <p className="text-xs text-green-700 mt-2">
                        {percentageUsed}% of budget
                    </p>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-purple-900">
                                Remaining
                            </p>
                            <p className="text-3xl font-bold text-purple-900 mt-2">
                                ${(totalBudgeted - totalSpent).toLocaleString()}
                            </p>
                        </div>
                        <Calendar className="h-10 w-10 text-purple-600" />
                    </div>
                    <p className="text-xs text-purple-700 mt-2">
                        {(100 - parseFloat(percentageUsed)).toFixed(1)}% available
                    </p>
                </div>
            </div>

            <div className="border rounded-lg p-6 space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">
                    Budget Settings
                </h3>

                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label htmlFor="monthlyBudget">Monthly Budget</Label>
                        <div className="relative">
                            <DollarSign className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <Input
                                id="monthlyBudget"
                                type="number"
                                value={budgetData.monthlyBudget}
                                onChange={(e) =>
                                    handleChange("monthlyBudget", e.target.value)
                                }
                                disabled={!isEditing}
                                className="pl-9"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="currency">Currency</Label>
                        <Select
                            value={budgetData.currency}
                            onValueChange={(value) =>
                                handleChange("currency", value)
                            }
                            disabled={!isEditing}
                        >
                            <SelectTrigger>
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="USD">USD ($)</SelectItem>
                                <SelectItem value="EUR">EUR (€)</SelectItem>
                                <SelectItem value="GBP">GBP (£)</SelectItem>
                                <SelectItem value="JPY">JPY (¥)</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="fiscalYearStart">
                            Fiscal Year Start
                        </Label>
                        <Select
                            value={budgetData.fiscalYearStart}
                            onValueChange={(value) =>
                                handleChange("fiscalYearStart", value)
                            }
                            disabled={!isEditing}
                        >
                            <SelectTrigger>
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="January">January</SelectItem>
                                <SelectItem value="April">April</SelectItem>
                                <SelectItem value="July">July</SelectItem>
                                <SelectItem value="October">October</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="approvalRequired">
                            Approval Required Above
                        </Label>
                        <div className="relative">
                            <DollarSign className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <Input
                                id="approvalRequired"
                                type="number"
                                value={budgetData.approvalRequired}
                                onChange={(e) =>
                                    handleChange(
                                        "approvalRequired",
                                        e.target.value
                                    )
                                }
                                disabled={!isEditing}
                                className="pl-9"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <div className="border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Expense Breakdown
                </h3>
                <div className="space-y-4">
                    {expenses.map((expense, index) => (
                        <div key={index} className="space-y-2">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-medium text-gray-900">
                                        {expense.category}
                                    </span>
                                    {expense.trend === "up" && (
                                        <TrendingUp className="h-4 w-4 text-red-500" />
                                    )}
                                    {expense.trend === "down" && (
                                        <TrendingDown className="h-4 w-4 text-green-500" />
                                    )}
                                </div>
                                <span className="text-sm text-gray-600">
                                    ${expense.spent.toLocaleString()} / $
                                    {expense.budgeted.toLocaleString()}
                                </span>
                            </div>
                            <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className={`absolute h-full ${
                                        expense.percentage > 90
                                            ? "bg-red-500"
                                            : expense.percentage > 70
                                            ? "bg-yellow-500"
                                            : "bg-green-500"
                                    }`}
                                    style={{ width: `${expense.percentage}%` }}
                                />
                            </div>
                            <p className="text-xs text-gray-500">
                                {expense.percentage}% used
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default BudgetAndCosting;
