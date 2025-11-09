import React, { useState, useEffect } from "react";
import { Building, Globe, Users, Edit2, Save, X } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
    DropdownSelect,
    DropdownSelectTrigger,
    DropdownSelectContent,
    DropdownSelectItem,
} from "../ui/dropdown-select";
import { useOrganizationUpdate } from "../../hooks/use-organization";
import { useToast } from "../../hooks/use-toast";
import { INDUSTRIES, COMPANY_SIZES } from "../../utils/constants";

const BasicDetails = ({ organization }) => {
    const { toast } = useToast();
    const updateOrganization = useOrganizationUpdate();
    const [isEditing, setIsEditing] = useState(false);
    const [isFieldEditing, setIsFieldEditing] = useState({});
    const [formData, setFormData] = useState({
        name: organization?.name || "",
        industry: organization?.industry || "",
        companySize: organization?.companySize || "",
        websiteUrl: organization?.websiteUrl || "",
    });

    // Update form data when organization changes
    useEffect(() => {
        if (organization) {
            setFormData({
                name: organization.name || "",
                industry: organization.industry || "",
                companySize: organization.companySize || "",
                websiteUrl: organization.websiteUrl || "",
            });
        }
    }, [organization]);

    const handleSave = async () => {
        try {
            await updateOrganization.mutateAsync({
                id: organization.id,
                data: formData,
            });
            toast({
                title: "Settings saved",
                description:
                    "Organization details have been updated successfully.",
            });
            setIsEditing(false);
            setIsFieldEditing({});
        } catch (error) {
            toast({
                variant: "destructive",
                title: "Error",
                description:
                    error.message ||
                    "Failed to update organization details. Please try again.",
            });
        }
    };

    const handleFieldSave = async (field) => {
        try {
            await updateOrganization.mutateAsync({
                id: organization.id,
                data: { [field]: formData[field] },
            });
            toast({
                title: "Field updated",
                description: `${field} has been updated successfully.`,
            });
            setIsFieldEditing({ ...isFieldEditing, [field]: false });
        } catch (error) {
            toast({
                variant: "destructive",
                title: "Error",
                description:
                    error.message ||
                    "Failed to update field. Please try again.",
            });
        }
    };

    const handleChange = (field, value) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
    };

    const handleCancel = () => {
        setFormData({
            name: organization.name || "",
            industry: organization.industry || "",
            companySize: organization.companySize || "",
            websiteUrl: organization.websiteUrl || "",
        });
        setIsEditing(false);
        setIsFieldEditing({});
    };

    const FieldWrapper = ({ field, label, icon: Icon, children }) => {
        const isFieldEditMode = isFieldEditing[field] || isEditing;
        const isReadOnly = !isFieldEditMode;

        return (
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <Label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                        {Icon && <Icon className="h-4 w-4 text-gray-500" />}
                        {label}
                    </Label>
                    {!isEditing && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                                setIsFieldEditing({
                                    ...isFieldEditing,
                                    [field]: true,
                                })
                            }
                            className="h-8 px-2"
                        >
                            <Edit2 className="h-4 w-4" />
                        </Button>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    <div className="flex-1">{children}</div>
                    {isFieldEditMode && !isEditing && (
                        <div className="flex gap-1">
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleFieldSave(field)}
                                className="h-8 px-2"
                            >
                                <Save className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() =>
                                    setIsFieldEditing({
                                        ...isFieldEditing,
                                        [field]: false,
                                    })
                                }
                                className="h-8 px-2"
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="space-y-6">
            <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900">
                    Basic Details
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                    Manage your organization's basic information
                </p>
            </div>

            <div className="border-t border-gray-200 pt-6">
                <div className="grid grid-cols-2 gap-6">
                    <FieldWrapper
                        field="name"
                        label="Organization Name"
                        icon={Building}
                    >
                        <Input
                            value={formData.name}
                            onChange={(e) =>
                                handleChange("name", e.target.value)
                            }
                            disabled={!isEditing && !isFieldEditing.name}
                            placeholder="Your organization name"
                            className="h-12"
                        />
                    </FieldWrapper>

                    <FieldWrapper
                        field="industry"
                        label="Industry"
                        icon={Building}
                    >
                        <DropdownSelect
                            value={formData.industry}
                            onValueChange={(value) =>
                                handleChange("industry", value)
                            }
                            disabled={!isEditing && !isFieldEditing.industry}
                        >
                            <DropdownSelectTrigger
                                disabled={
                                    !isEditing && !isFieldEditing.industry
                                }
                                className={`h-12 ${
                                    !isEditing && !isFieldEditing.industry
                                        ? "bg-gray-50"
                                        : ""
                                }`}
                                placeholder="Select industry"
                            >
                                {INDUSTRIES.find(
                                    (i) => i.value === formData.industry
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
                    </FieldWrapper>

                    <FieldWrapper
                        field="companySize"
                        label="Company Size"
                        icon={Users}
                    >
                        <DropdownSelect
                            value={formData.companySize}
                            onValueChange={(value) =>
                                handleChange("companySize", value)
                            }
                            disabled={!isEditing && !isFieldEditing.companySize}
                        >
                            <DropdownSelectTrigger
                                disabled={
                                    !isEditing && !isFieldEditing.companySize
                                }
                                className={`h-12 ${
                                    !isEditing && !isFieldEditing.companySize
                                        ? "bg-gray-50"
                                        : ""
                                }`}
                                placeholder="Select company size"
                            >
                                {COMPANY_SIZES.find(
                                    (s) => s.value === formData.companySize
                                )?.label || "Select company size"}
                            </DropdownSelectTrigger>
                            <DropdownSelectContent>
                                {COMPANY_SIZES.map((size) => (
                                    <DropdownSelectItem
                                        key={size.value}
                                        value={size.value}
                                    >
                                        {size.label}
                                    </DropdownSelectItem>
                                ))}
                            </DropdownSelectContent>
                        </DropdownSelect>
                    </FieldWrapper>

                    <FieldWrapper
                        field="websiteUrl"
                        label="Website URL"
                        icon={Globe}
                    >
                        <Input
                            type="url"
                            value={formData.websiteUrl}
                            onChange={(e) =>
                                handleChange("websiteUrl", e.target.value)
                            }
                            disabled={!isEditing && !isFieldEditing.websiteUrl}
                            placeholder="https://example.com"
                            className="h-12"
                        />
                    </FieldWrapper>
                </div>
            </div>
        </div>
    );
};

export default BasicDetails;
