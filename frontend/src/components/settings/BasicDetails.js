import React, { useState } from "react";
import { Building, Mail, Globe, MapPin, Users, Save } from "lucide-react";
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
import { Textarea } from "../ui/textarea";
import { useToast } from "../../hooks/use-toast";

const BasicDetails = () => {
    const { toast } = useToast();
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        name: "Acme Corporation",
        email: "contact@acmecorp.com",
        website: "https://acmecorp.com",
        industry: "Technology",
        companySize: "51-200",
        description:
            "Leading provider of innovative technology solutions for businesses worldwide.",
        address: "123 Tech Street, San Francisco, CA 94105",
        phone: "+1 (555) 123-4567",
    });

    const handleSave = () => {
        toast({
            title: "Settings saved",
            description: "Organization details have been updated successfully.",
        });
        setIsEditing(false);
    };

    const handleChange = (field, value) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-gray-900">
                        Basic Details
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Manage your organization's basic information
                    </p>
                </div>
                {!isEditing ? (
                    <Button onClick={() => setIsEditing(true)}>
                        Edit Details
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

            <div className="border-t pt-6 space-y-6">
                <div className="space-y-2">
                    <Label htmlFor="name">
                        <Building className="inline h-4 w-4 mr-2" />
                        Organization Name
                    </Label>
                    <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => handleChange("name", e.target.value)}
                        disabled={!isEditing}
                        placeholder="Your organization name"
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="email">
                        <Mail className="inline h-4 w-4 mr-2" />
                        Contact Email
                    </Label>
                    <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleChange("email", e.target.value)}
                        disabled={!isEditing}
                        placeholder="contact@example.com"
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                        id="phone"
                        value={formData.phone}
                        onChange={(e) => handleChange("phone", e.target.value)}
                        disabled={!isEditing}
                        placeholder="+1 (555) 123-4567"
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="website">
                        <Globe className="inline h-4 w-4 mr-2" />
                        Website
                    </Label>
                    <Input
                        id="website"
                        value={formData.website}
                        onChange={(e) =>
                            handleChange("website", e.target.value)
                        }
                        disabled={!isEditing}
                        placeholder="https://example.com"
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="industry">Industry</Label>
                    <Select
                        value={formData.industry}
                        onValueChange={(value) =>
                            handleChange("industry", value)
                        }
                        disabled={!isEditing}
                    >
                        <SelectTrigger>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="Technology">Technology</SelectItem>
                            <SelectItem value="Healthcare">Healthcare</SelectItem>
                            <SelectItem value="Finance">Finance</SelectItem>
                            <SelectItem value="Education">Education</SelectItem>
                            <SelectItem value="Retail">Retail</SelectItem>
                            <SelectItem value="Other">Other</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-2">
                    <Label htmlFor="companySize">
                        <Users className="inline h-4 w-4 mr-2" />
                        Company Size
                    </Label>
                    <Select
                        value={formData.companySize}
                        onValueChange={(value) =>
                            handleChange("companySize", value)
                        }
                        disabled={!isEditing}
                    >
                        <SelectTrigger>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="1-10">1-10 employees</SelectItem>
                            <SelectItem value="11-50">11-50 employees</SelectItem>
                            <SelectItem value="51-200">51-200 employees</SelectItem>
                            <SelectItem value="201-1000">
                                201-1000 employees
                            </SelectItem>
                            <SelectItem value="1000+">1000+ employees</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-2">
                    <Label htmlFor="address">
                        <MapPin className="inline h-4 w-4 mr-2" />
                        Address
                    </Label>
                    <Input
                        id="address"
                        value={formData.address}
                        onChange={(e) =>
                            handleChange("address", e.target.value)
                        }
                        disabled={!isEditing}
                        placeholder="Your organization address"
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                        id="description"
                        value={formData.description}
                        onChange={(e) =>
                            handleChange("description", e.target.value)
                        }
                        disabled={!isEditing}
                        placeholder="Brief description of your organization"
                        rows={4}
                    />
                </div>
            </div>
        </div>
    );
};

export default BasicDetails;
