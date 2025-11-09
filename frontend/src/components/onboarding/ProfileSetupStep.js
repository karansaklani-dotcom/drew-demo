import React, { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
    DropdownSelect,
    DropdownSelectTrigger,
    DropdownSelectContent,
    DropdownSelectItem,
} from "../ui/dropdown-select";
import { useToast } from "../../hooks/use-toast";
import { ROLES } from "../../utils/constants";

export const ProfileSetupStep = ({
    profileData,
    setProfileData,
    onContinue,
    onBack,
    showBack = true,
}) => {
    const [errors, setErrors] = useState({});
    const { toast } = useToast();

    const validate = () => {
        const newErrors = {};

        if (!profileData.firstName || profileData.firstName.trim() === "") {
            newErrors.firstName = "First name is required";
        }

        if (!profileData.lastName || profileData.lastName.trim() === "") {
            newErrors.lastName = "Last name is required";
        }

        if (!profileData.role) {
            newErrors.role = "Role/Department is required";
        }

        setErrors(newErrors);

        // Show toast for first error
        const firstError = Object.values(newErrors)[0];
        if (firstError) {
            toast({
                variant: "destructive",
                title: "Validation Error",
                description: firstError,
            });
        }

        return Object.keys(newErrors).length === 0;
    };

    const handleContinue = () => {
        if (validate()) {
            onContinue();
        }
    };

    return (
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h2 className="text-3xl font-bold mb-2">Complete your profile</h2>
            <p className="text-gray-600 mb-8">
                Help us personalize your experience
            </p>

            <div className="space-y-6">
                <div className="space-y-2">
                    <Label htmlFor="firstName">
                        First name <span className="text-red-500">*</span>
                    </Label>
                    <Input
                        id="firstName"
                        placeholder="John"
                        value={profileData.firstName}
                        onChange={(e) => {
                            setProfileData({
                                ...profileData,
                                firstName: e.target.value,
                            });
                            if (errors.firstName) {
                                const { firstName, ...rest } = errors;
                                setErrors(rest);
                            }
                        }}
                        className={`h-12 ${
                            errors.firstName ? "border-red-500" : ""
                        }`}
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="lastName">
                        Last name <span className="text-red-500">*</span>
                    </Label>
                    <Input
                        id="lastName"
                        placeholder="Doe"
                        value={profileData.lastName}
                        onChange={(e) => {
                            setProfileData({
                                ...profileData,
                                lastName: e.target.value,
                            });
                            if (errors.lastName) {
                                const { lastName, ...rest } = errors;
                                setErrors(rest);
                            }
                        }}
                        className={`h-12 ${
                            errors.lastName ? "border-red-500" : ""
                        }`}
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="role">
                        Role/Department <span className="text-red-500">*</span>
                    </Label>
                    <DropdownSelect
                        value={profileData.role}
                        onValueChange={(value) => {
                            setProfileData({
                                ...profileData,
                                role: value,
                            });
                            if (errors.role) {
                                const { role, ...rest } = errors;
                                setErrors(rest);
                            }
                        }}
                    >
                        <DropdownSelectTrigger
                            className={`h-12 ${
                                errors.role ? "border-red-500" : ""
                            }`}
                            placeholder="Select your role"
                        >
                            {ROLES.find((r) => r.value === profileData.role)
                                ?.label || "Select your role"}
                        </DropdownSelectTrigger>
                        <DropdownSelectContent>
                            {ROLES.map((role) => (
                                <DropdownSelectItem
                                    key={role.value}
                                    value={role.value}
                                >
                                    {role.label}
                                </DropdownSelectItem>
                            ))}
                        </DropdownSelectContent>
                    </DropdownSelect>
                </div>
            </div>

            <div className="flex gap-4 mt-8">
                {showBack && onBack && (
                    <Button
                        variant="outline"
                        onClick={onBack}
                        className="flex-1 h-12"
                    >
                        Back
                    </Button>
                )}
                <Button
                    onClick={handleContinue}
                    className={`${
                        showBack && onBack ? "flex-1" : "w-full"
                    } h-12 bg-black hover:bg-gray-800 text-white`}
                >
                    Continue
                </Button>
            </div>
        </div>
    );
};
