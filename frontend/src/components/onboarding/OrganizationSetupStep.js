import React, { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { RadioGroup, RadioGroupItem } from "../ui/radio-group";
import {
    DropdownSelect,
    DropdownSelectTrigger,
    DropdownSelectContent,
    DropdownSelectItem,
} from "../ui/dropdown-select";
import { useToast } from "../../hooks/use-toast";
import { INDUSTRIES, COMPANY_SIZES } from "../../utils/constants";

export const OrganizationSetupStep = ({
    orgData,
    setOrgData,
    onContinue,
    onSkip,
}) => {
    const [errors, setErrors] = useState({});
    const { toast } = useToast();

    const validate = () => {
        const newErrors = {};

        if (!orgData.name || orgData.name.trim() === "") {
            newErrors.name = "Organization name is required";
        }

        if (!orgData.industry) {
            newErrors.industry = "Industry is required";
        }

        if (!orgData.companySize) {
            newErrors.companySize = "Company size is required";
        }

        if (orgData.website && orgData.website.trim() !== "") {
            try {
                new URL(orgData.website);
            } catch (e) {
                newErrors.website = "Please enter a valid URL";
            }
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
            <h2 className="text-3xl font-bold mb-2">
                Set up your organization
            </h2>
            <p className="text-gray-600 mb-8">Tell us about your company</p>

            <div className="space-y-6">
                <div className="space-y-2">
                    <Label htmlFor="orgName">
                        Organization name{" "}
                        <span className="text-red-500">*</span>
                    </Label>
                    <Input
                        id="orgName"
                        placeholder="Acme Inc."
                        value={orgData.name}
                        onChange={(e) => {
                            setOrgData({
                                ...orgData,
                                name: e.target.value,
                            });
                            if (errors.name) {
                                const { name, ...rest } = errors;
                                setErrors(rest);
                            }
                        }}
                        className={`h-12 ${
                            errors.name ? "border-red-500" : ""
                        }`}
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="industry">
                        Industry <span className="text-red-500">*</span>
                    </Label>
                    <DropdownSelect
                        value={orgData.industry}
                        onValueChange={(value) => {
                            setOrgData({
                                ...orgData,
                                industry: value,
                            });
                            if (errors.industry) {
                                const { industry, ...rest } = errors;
                                setErrors(rest);
                            }
                        }}
                    >
                        <DropdownSelectTrigger
                            className={`h-12 ${
                                errors.industry ? "border-red-500" : ""
                            }`}
                            placeholder="Select industry"
                        >
                            {INDUSTRIES.find(
                                (i) => i.value === orgData.industry
                            )?.label || "Select industry"}
                        </DropdownSelectTrigger>
                        <DropdownSelectContent>
                            {INDUSTRIES.map((industry) => (
                                <DropdownSelectItem
                                    key={industry.value}
                                    value={industry.value}
                                >
                                    {industry.label}
                                </DropdownSelectItem>
                            ))}
                        </DropdownSelectContent>
                    </DropdownSelect>
                </div>

                <div className="space-y-2">
                    <Label>
                        Company size <span className="text-red-500">*</span>
                    </Label>
                    <RadioGroup
                        value={orgData.companySize}
                        onValueChange={(value) => {
                            setOrgData({
                                ...orgData,
                                companySize: value,
                            });
                            if (errors.companySize) {
                                const { companySize, ...rest } = errors;
                                setErrors(rest);
                            }
                        }}
                        className="space-y-3"
                    >
                        {COMPANY_SIZES.map((size, index) => (
                            <div
                                key={size.value}
                                className={`flex items-center space-x-3 border rounded-lg p-4 hover:bg-gray-50 cursor-pointer ${
                                    errors.companySize ? "border-red-500" : ""
                                }`}
                            >
                                <RadioGroupItem
                                    value={size.value}
                                    id={`size${index + 1}`}
                                />
                                <Label
                                    htmlFor={`size${index + 1}`}
                                    className="flex-1 cursor-pointer"
                                >
                                    {size.label}
                                </Label>
                            </div>
                        ))}
                    </RadioGroup>
                </div>

                <div className="space-y-2">
                    <Label htmlFor="website">Website URL (optional)</Label>
                    <Input
                        id="website"
                        type="url"
                        placeholder="https://example.com"
                        value={orgData.website}
                        onChange={(e) => {
                            setOrgData({
                                ...orgData,
                                website: e.target.value,
                            });
                            if (errors.website) {
                                const { website, ...rest } = errors;
                                setErrors(rest);
                            }
                        }}
                        className={`h-12 ${
                            errors.website ? "border-red-500" : ""
                        }`}
                    />
                </div>
            </div>

            <div className="flex gap-4 mt-8">
                <Button
                    variant="outline"
                    onClick={onSkip}
                    className="flex-1 h-12"
                >
                    Skip
                </Button>
                <Button
                    onClick={handleContinue}
                    className="flex-1 h-12 bg-black hover:bg-gray-800 text-white"
                >
                    Continue
                </Button>
            </div>
        </div>
    );
};
