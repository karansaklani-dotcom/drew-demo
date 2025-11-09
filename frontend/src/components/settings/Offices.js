import React, { useState } from "react";
import { Plus, Building2 } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "../ui/dialog";
import {
    DropdownSelect,
    DropdownSelectTrigger,
    DropdownSelectContent,
    DropdownSelectItem,
} from "../ui/dropdown-select";
import AddressInput from "./AddressInput";
import OfficeCard from "./OfficeCard";
import { useToast } from "../../hooks/use-toast";
import { ChevronLeft, ChevronRight } from "lucide-react";

const PARKING_OPTIONS = [
    { value: "available", label: "Available" },
    { value: "limited", label: "Limited" },
    { value: "not_available", label: "Not Available" },
    { value: "street_only", label: "Street Parking Only" },
];

const MEETING_ROOM_OPTIONS = [
    { value: "available", label: "Available" },
    { value: "limited", label: "Limited" },
    { value: "not_available", label: "Not Available" },
    { value: "booking_required", label: "Booking Required" },
];

const YES_NO_OPTIONS = [
    { value: "yes", label: "Yes" },
    { value: "no", label: "No" },
];

const Offices = () => {
    const { toast } = useToast();
    const [offices, setOffices] = useState([
        {
            id: 1,
            title: "Headquarters",
            address: {
                line1: "123 Tech Street",
                line2: "Suite 100",
                city: "San Francisco",
                country: "United States",
                pincode: "94105",
            },
            parking: "available",
            parkingContext: "Free parking for employees",
            meetingRooms: "available",
            meetingRoomsContext: "5 meeting rooms available, booking required",
            additionalContext: "",
            checkInRequired: "yes",
            idRequired: "yes",
            escortRequired: "yes",
            securityContext: "Visitor check-in at reception desk",
        },
        {
            id: 2,
            title: "New York Office",
            address: {
                line1: "456 Business Ave",
                line2: "",
                city: "New York",
                country: "United States",
                pincode: "10001",
            },
            parking: "limited",
            parkingContext: "Street parking only",
            meetingRooms: "available",
            meetingRoomsContext: "3 meeting rooms available",
            additionalContext: "",
            checkInRequired: "yes",
            idRequired: "yes",
            escortRequired: "yes",
            securityContext: "Check-in at security desk, ID required",
        },
    ]);

    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingOffice, setEditingOffice] = useState(null);
    const [currentStep, setCurrentStep] = useState(1);
    const [formData, setFormData] = useState({
        title: "",
        address: {
            line1: "",
            line2: "",
            city: "",
            country: "",
            pincode: "",
        },
        parking: "",
        parkingContext: "",
        meetingRooms: "",
        meetingRoomsContext: "",
        additionalContext: "",
        checkInRequired: "",
        idRequired: "",
        escortRequired: "",
        securityContext: "",
    });

    const handleOpenDialog = (office = null) => {
        if (office) {
            setEditingOffice(office);
            setFormData({
                title: office.title || "",
                address: office.address || {
                    line1: "",
                    line2: "",
                    city: "",
                    country: "",
                    pincode: "",
                },
                parking: office.parking || "",
                parkingContext: office.parkingContext || "",
                meetingRooms: office.meetingRooms || "",
                meetingRoomsContext: office.meetingRoomsContext || "",
                additionalContext: office.additionalContext || "",
                checkInRequired: office.checkInRequired || "",
                idRequired: office.idRequired || "",
                escortRequired: office.escortRequired || "",
                securityContext: office.securityContext || "",
            });
            setCurrentStep(1);
        } else {
            setEditingOffice(null);
            setFormData({
                title: "",
                address: {
                    line1: "",
                    line2: "",
                    city: "",
                    country: "",
                    pincode: "",
                },
                parking: "",
                parkingContext: "",
                meetingRooms: "",
                meetingRoomsContext: "",
                additionalContext: "",
                checkInRequired: "",
                idRequired: "",
                escortRequired: "",
                securityContext: "",
            });
            setCurrentStep(1);
        }
        setIsDialogOpen(true);
    };

    const handleCloseDialog = () => {
        setIsDialogOpen(false);
        setEditingOffice(null);
        setCurrentStep(1);
        setFormData({
            title: "",
            address: {
                line1: "",
                line2: "",
                city: "",
                country: "",
                pincode: "",
            },
            parking: "",
            parkingContext: "",
            meetingRooms: "",
            meetingRoomsContext: "",
            additionalContext: "",
            checkInRequired: "",
            idRequired: "",
            escortRequired: "",
            securityContext: "",
        });
    };

    const handleNext = () => {
        if (currentStep === 1) {
            // Validate step 1
            if (
                !formData.title ||
                !formData.address.line1 ||
                !formData.address.city ||
                !formData.address.country ||
                !formData.address.pincode
            ) {
                toast({
                    variant: "destructive",
                    title: "Validation Error",
                    description:
                        "Title, Address Line 1, City, Country, and Pincode are required fields.",
                });
                return;
            }
        }
        if (currentStep < 3) {
            setCurrentStep(currentStep + 1);
        }
    };

    const handlePrevious = () => {
        if (currentStep > 1) {
            setCurrentStep(currentStep - 1);
        }
    };

    const handleSave = () => {
        // Final validation
        if (
            !formData.title ||
            !formData.address.line1 ||
            !formData.address.city ||
            !formData.address.country ||
            !formData.address.pincode
        ) {
            toast({
                variant: "destructive",
                title: "Validation Error",
                description:
                    "Title, Address Line 1, City, Country, and Pincode are required fields.",
            });
            return;
        }

        if (editingOffice) {
            setOffices(
                offices.map((office) =>
                    office.id === editingOffice.id
                        ? { ...editingOffice, ...formData }
                        : office
                )
            );
            toast({
                title: "Office updated",
                description: "Office details have been updated successfully.",
            });
        } else {
            const newOffice = {
                id: offices.length + 1,
                ...formData,
            };
            setOffices([...offices, newOffice]);
            toast({
                title: "Office added",
                description: "New office has been added successfully.",
            });
        }
        handleCloseDialog();
    };

    const handleDelete = (officeId) => {
        setOffices(offices.filter((office) => office.id !== officeId));
        toast({
            title: "Office deleted",
            description: "Office has been removed successfully.",
        });
    };

    const handleChange = (field, value) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
    };

    const handleAddressChange = (address) => {
        setFormData((prev) => ({ ...prev, address }));
    };

    const renderStepContent = () => {
        switch (currentStep) {
            case 1:
                return (
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="title">
                                Title <span className="text-red-500">*</span>
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                A descriptive name for this office location
                            </p>
                            <Input
                                id="title"
                                value={formData.title}
                                onChange={(e) =>
                                    handleChange("title", e.target.value)
                                }
                                placeholder="e.g., Headquarters, New York Office"
                            />
                        </div>

                        <AddressInput
                            value={formData.address}
                            onChange={handleAddressChange}
                        />
                    </div>
                );
            case 2:
                return (
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="meetingRooms">
                                Meeting Room Availability{" "}
                                <span className="text-red-500">*</span>
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                Select the availability of meeting rooms at this
                                office
                            </p>
                            <DropdownSelect
                                value={formData.meetingRooms}
                                onValueChange={(value) =>
                                    handleChange("meetingRooms", value)
                                }
                            >
                                <DropdownSelectTrigger
                                    className="h-12"
                                    placeholder="Select meeting room availability"
                                >
                                    {MEETING_ROOM_OPTIONS.find(
                                        (opt) =>
                                            opt.value === formData.meetingRooms
                                    )?.label ||
                                        "Select meeting room availability"}
                                </DropdownSelectTrigger>
                                <DropdownSelectContent>
                                    {MEETING_ROOM_OPTIONS.map((option) => (
                                        <DropdownSelectItem
                                            key={option.value}
                                            value={option.value}
                                        >
                                            {option.label}
                                        </DropdownSelectItem>
                                    ))}
                                </DropdownSelectContent>
                            </DropdownSelect>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="meetingRoomsContext">
                                Meeting Room Details
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                Provide additional details about meeting room
                                availability, booking requirements, or capacity
                            </p>
                            <Textarea
                                id="meetingRoomsContext"
                                value={formData.meetingRoomsContext}
                                onChange={(e) =>
                                    handleChange(
                                        "meetingRoomsContext",
                                        e.target.value
                                    )
                                }
                                placeholder="e.g., 5 meeting rooms available, booking required"
                                rows={2}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="parking">
                                Parking <span className="text-red-500">*</span>
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                Select the parking availability at this office
                                location
                            </p>
                            <DropdownSelect
                                value={formData.parking}
                                onValueChange={(value) =>
                                    handleChange("parking", value)
                                }
                            >
                                <DropdownSelectTrigger
                                    className="h-12"
                                    placeholder="Select parking availability"
                                >
                                    {PARKING_OPTIONS.find(
                                        (opt) => opt.value === formData.parking
                                    )?.label || "Select parking availability"}
                                </DropdownSelectTrigger>
                                <DropdownSelectContent>
                                    {PARKING_OPTIONS.map((option) => (
                                        <DropdownSelectItem
                                            key={option.value}
                                            value={option.value}
                                        >
                                            {option.label}
                                        </DropdownSelectItem>
                                    ))}
                                </DropdownSelectContent>
                            </DropdownSelect>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="parkingContext">
                                Parking Details
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                Provide additional details about parking, such
                                as cost, restrictions, or special instructions
                            </p>
                            <Textarea
                                id="parkingContext"
                                value={formData.parkingContext}
                                onChange={(e) =>
                                    handleChange(
                                        "parkingContext",
                                        e.target.value
                                    )
                                }
                                placeholder="e.g., Free parking for employees"
                                rows={2}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="additionalContext">
                                Additional Context
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                Any other relevant information about this office
                                location, such as nearby amenities or
                                accessibility features
                            </p>
                            <Textarea
                                id="additionalContext"
                                value={formData.additionalContext}
                                onChange={(e) =>
                                    handleChange(
                                        "additionalContext",
                                        e.target.value
                                    )
                                }
                                placeholder="Any additional context about the office"
                                rows={2}
                            />
                        </div>
                    </div>
                );
            case 3:
                return (
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="checkInRequired">
                                Check-in Required{" "}
                                <span className="text-red-500">*</span>
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                Indicate if visitors must check in at reception
                                or security desk
                            </p>
                            <DropdownSelect
                                value={formData.checkInRequired}
                                onValueChange={(value) =>
                                    handleChange("checkInRequired", value)
                                }
                            >
                                <DropdownSelectTrigger
                                    className="h-12"
                                    placeholder="Select check-in requirement"
                                >
                                    {YES_NO_OPTIONS.find(
                                        (opt) =>
                                            opt.value ===
                                            formData.checkInRequired
                                    )?.label || "Select check-in requirement"}
                                </DropdownSelectTrigger>
                                <DropdownSelectContent>
                                    {YES_NO_OPTIONS.map((option) => (
                                        <DropdownSelectItem
                                            key={option.value}
                                            value={option.value}
                                        >
                                            {option.label}
                                        </DropdownSelectItem>
                                    ))}
                                </DropdownSelectContent>
                            </DropdownSelect>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="idRequired">
                                ID Required{" "}
                                <span className="text-red-500">*</span>
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                Indicate if visitors must present identification
                                to enter
                            </p>
                            <DropdownSelect
                                value={formData.idRequired}
                                onValueChange={(value) =>
                                    handleChange("idRequired", value)
                                }
                            >
                                <DropdownSelectTrigger
                                    className="h-12"
                                    placeholder="Select ID requirement"
                                >
                                    {YES_NO_OPTIONS.find(
                                        (opt) =>
                                            opt.value === formData.idRequired
                                    )?.label || "Select ID requirement"}
                                </DropdownSelectTrigger>
                                <DropdownSelectContent>
                                    {YES_NO_OPTIONS.map((option) => (
                                        <DropdownSelectItem
                                            key={option.value}
                                            value={option.value}
                                        >
                                            {option.label}
                                        </DropdownSelectItem>
                                    ))}
                                </DropdownSelectContent>
                            </DropdownSelect>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="escortRequired">
                                Escort Required{" "}
                                <span className="text-red-500">*</span>
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                Indicate if visitors must be escorted by an
                                employee while on premises
                            </p>
                            <DropdownSelect
                                value={formData.escortRequired}
                                onValueChange={(value) =>
                                    handleChange("escortRequired", value)
                                }
                            >
                                <DropdownSelectTrigger
                                    className="h-12"
                                    placeholder="Select escort requirement"
                                >
                                    {YES_NO_OPTIONS.find(
                                        (opt) =>
                                            opt.value ===
                                            formData.escortRequired
                                    )?.label || "Select escort requirement"}
                                </DropdownSelectTrigger>
                                <DropdownSelectContent>
                                    {YES_NO_OPTIONS.map((option) => (
                                        <DropdownSelectItem
                                            key={option.value}
                                            value={option.value}
                                        >
                                            {option.label}
                                        </DropdownSelectItem>
                                    ))}
                                </DropdownSelectContent>
                            </DropdownSelect>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="securityContext">
                                Security Context
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                Provide additional security information, such as
                                check-in procedures, visitor policies, or
                                special requirements
                            </p>
                            <Textarea
                                id="securityContext"
                                value={formData.securityContext}
                                onChange={(e) =>
                                    handleChange(
                                        "securityContext",
                                        e.target.value
                                    )
                                }
                                placeholder="e.g., Visitor check-in at reception desk"
                                rows={2}
                            />
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                        Offices
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Manage your organization's office locations
                    </p>
                </div>
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                        <Button
                            className="bg-black hover:bg-gray-800 text-white"
                            onClick={() => handleOpenDialog()}
                        >
                            <Plus className="mr-2 h-4 w-4" />
                            Add Office
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
                        <DialogHeader>
                            <DialogTitle>
                                {editingOffice
                                    ? "Edit Office"
                                    : "Add New Office"}
                            </DialogTitle>
                            <DialogDescription>
                                {editingOffice
                                    ? "Update office details below"
                                    : "Fill in the details to add a new office"}
                            </DialogDescription>
                        </DialogHeader>

                        {/* Step Indicator - Center Aligned */}
                        <div className="py-4">
                            <div className="flex items-center justify-center gap-8">
                                {[1, 2, 3].map((step) => (
                                    <div
                                        key={step}
                                        className="flex items-center"
                                    >
                                        <div className="flex flex-col items-center">
                                            <div
                                                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                                                    currentStep >= step
                                                        ? "bg-black text-white"
                                                        : "bg-gray-200 text-gray-600"
                                                }`}
                                            >
                                                {step}
                                            </div>
                                            <p
                                                className={`text-xs mt-2 text-center ${
                                                    currentStep >= step
                                                        ? "text-gray-900 font-medium"
                                                        : "text-gray-500"
                                                }`}
                                            >
                                                {step === 1 &&
                                                    "Title & Address"}
                                                {step === 2 &&
                                                    "Execution Context"}
                                                {step === 3 &&
                                                    "Security Details"}
                                            </p>
                                        </div>
                                        {step < 3 && (
                                            <div
                                                className={`w-16 h-0.5 mx-4 ${
                                                    currentStep > step
                                                        ? "bg-black"
                                                        : "bg-gray-200"
                                                }`}
                                            />
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Step Content */}
                        <div className="py-4 min-h-[300px]">
                            {renderStepContent()}
                        </div>

                        <DialogFooter>
                            <div className="flex items-center justify-between w-full">
                                <Button
                                    variant="outline"
                                    onClick={handlePrevious}
                                    disabled={currentStep === 1}
                                >
                                    <ChevronLeft className="mr-2 h-4 w-4" />
                                    Previous
                                </Button>
                                <div className="flex gap-2">
                                    <Button
                                        variant="outline"
                                        onClick={handleCloseDialog}
                                    >
                                        Cancel
                                    </Button>
                                    {currentStep < 3 ? (
                                        <Button
                                            onClick={handleNext}
                                            className="bg-black hover:bg-gray-800 text-white"
                                        >
                                            Next
                                            <ChevronRight className="ml-2 h-4 w-4" />
                                        </Button>
                                    ) : (
                                        <Button
                                            onClick={handleSave}
                                            className="bg-black hover:bg-gray-800 text-white"
                                        >
                                            {editingOffice ? "Update" : "Add"}{" "}
                                            Office
                                        </Button>
                                    )}
                                </div>
                            </div>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Offices List */}
            {offices.length === 0 ? (
                <div className="border border-gray-200 rounded-lg p-12 text-center bg-gray-50">
                    <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-2">No offices added yet</p>
                    <p className="text-sm text-gray-500">
                        Click "Add Office" to get started
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-2 gap-4">
                    {offices.map((office) => (
                        <OfficeCard
                            key={office.id}
                            office={office}
                            onEdit={handleOpenDialog}
                            onDelete={handleDelete}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default Offices;
