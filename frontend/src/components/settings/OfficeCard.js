import React, { useState } from "react";
import { MapPin, Edit2, Trash2, Building2, ChevronDown, X } from "lucide-react";
import { Button } from "../ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";

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

const formatAddress = (address) => {
    if (typeof address === "string") {
        return address;
    }
    const parts = [
        address.line1,
        address.line2,
        address.city,
        address.pincode,
        address.country,
    ].filter(Boolean);
    return parts.join(", ");
};

const OfficeCard = ({ office, onEdit, onDelete }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const addressString = formatAddress(office.address);
    const googleMapsApiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || "";
    const mapImageUrl = googleMapsApiKey
        ? `https://maps.googleapis.com/maps/api/staticmap?center=${encodeURIComponent(
              addressString
          )}&zoom=15&size=600x400&markers=color:red|${encodeURIComponent(
              addressString
          )}&key=${googleMapsApiKey}`
        : null;

    return (
        <>
            <div className="border border-gray-200 rounded-lg overflow-hidden bg-white hover:border-gray-300 transition-colors">
                {/* Collapsed State - Centered Layout */}
                <div className="p-6 h-full flex flex-col">
                    <div className="flex flex-col items-center text-center flex-1">
                        {/* Map Preview - Centered Square */}
                        <div className="w-32 h-32 relative bg-gray-100 rounded-lg overflow-hidden mb-4">
                            {mapImageUrl ? (
                                <img
                                    src={mapImageUrl}
                                    alt={`Map of ${office.title}`}
                                    className="absolute inset-0 w-full h-full object-cover"
                                    onError={(e) => {
                                        e.target.src =
                                            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='128' height='128'%3E%3Crect fill='%23f3f4f6' width='128' height='128'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%239ca3af' font-family='sans-serif' font-size='14'%3EMap Preview%3C/text%3E%3C/svg%3E";
                                    }}
                                />
                            ) : (
                                <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-gray-100">
                                    <div className="text-center">
                                        <MapPin className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                                        <p className="text-xs text-gray-500">
                                            Map Preview
                                        </p>
                                    </div>
                                </div>
                            )}
                            <div className="absolute top-2 left-2">
                                <div className="bg-white rounded-full p-1.5 shadow-md">
                                    <MapPin className="h-4 w-4 text-red-600" />
                                </div>
                            </div>
                        </div>

                        {/* Title and Address - Centered */}
                        <div className="mb-4">
                            <div className="flex items-center gap-2 mb-2 justify-center">
                                <Building2 className="h-5 w-5 text-gray-700" />
                                <h3 className="text-lg font-semibold text-gray-900">
                                    {office.title}
                                </h3>
                            </div>
                            <div className="flex items-center gap-2 justify-center">
                                <MapPin className="h-5 w-5 text-gray-700 flex-shrink-0" />
                                <p className="text-sm text-gray-600">
                                    {addressString}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* View More Button - Always at bottom */}
                    <div className="mt-auto">
                        <Button
                            variant="outline"
                            onClick={() => setIsModalOpen(true)}
                            className="w-full border-gray-300"
                        >
                            View More
                            <ChevronDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </div>

            {/* Modal with Office Details */}
            <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
                <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="text-2xl font-bold">
                            {office.title}
                        </DialogTitle>
                    </DialogHeader>

                    <div className="mt-4 space-y-6">
                        {/* Map and Address Section */}
                        <div className="grid grid-cols-2 gap-6">
                            {/* Map Preview */}
                            <div className="relative bg-gray-100 rounded-lg overflow-hidden h-64">
                                {mapImageUrl ? (
                                    <img
                                        src={mapImageUrl}
                                        alt={`Map of ${office.title}`}
                                        className="absolute inset-0 w-full h-full object-cover"
                                        onError={(e) => {
                                            e.target.src =
                                                "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='600' height='400'%3E%3Crect fill='%23f3f4f6' width='600' height='400'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%239ca3af' font-family='sans-serif' font-size='14'%3EMap Preview%3C/text%3E%3C/svg%3E";
                                        }}
                                    />
                                ) : (
                                    <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-gray-100">
                                        <div className="text-center">
                                            <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                                            <p className="text-sm text-gray-500">
                                                Map Preview
                                            </p>
                                        </div>
                                    </div>
                                )}
                                <div className="absolute top-3 left-3">
                                    <div className="bg-white rounded-full p-2 shadow-md">
                                        <MapPin className="h-5 w-5 text-red-600" />
                                    </div>
                                </div>
                            </div>

                            {/* Address Details */}
                            <div className="space-y-4">
                                <div>
                                    <h3 className="text-sm font-medium text-gray-700 mb-0">
                                        Address
                                    </h3>
                                    <div className="flex items-start gap-2">
                                        <MapPin className="h-5 w-5 text-gray-700 mt-0.5 flex-shrink-0" />
                                        <p className="text-sm text-gray-600">
                                            {addressString}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex gap-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => {
                                            setIsModalOpen(false);
                                            onEdit(office);
                                        }}
                                    >
                                        <Edit2 className="mr-2 h-4 w-4" />
                                        Edit
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => {
                                            setIsModalOpen(false);
                                            onDelete(office.id);
                                        }}
                                        className="text-red-600 hover:text-red-700"
                                    >
                                        <Trash2 className="mr-2 h-4 w-4" />
                                        Delete
                                    </Button>
                                </div>
                            </div>
                        </div>

                        {/* Additional Details */}
                        <div className="grid grid-cols-2 gap-6">
                            {/* Left Column */}
                            <div className="space-y-4">
                                {office.parking && (
                                    <div>
                                        <p className="text-xs font-medium text-gray-700 mb-0">
                                            Parking
                                        </p>
                                        <p className="text-sm text-gray-600">
                                            {
                                                PARKING_OPTIONS.find(
                                                    (opt) =>
                                                        opt.value ===
                                                        office.parking
                                                )?.label
                                            }
                                            {office.parkingContext &&
                                                ` - ${office.parkingContext}`}
                                        </p>
                                    </div>
                                )}

                                {office.meetingRooms && (
                                    <div>
                                        <p className="text-xs font-medium text-gray-700 mb-0">
                                            Meeting Rooms
                                        </p>
                                        <p className="text-sm text-gray-600">
                                            {
                                                MEETING_ROOM_OPTIONS.find(
                                                    (opt) =>
                                                        opt.value ===
                                                        office.meetingRooms
                                                )?.label
                                            }
                                            {office.meetingRoomsContext &&
                                                ` - ${office.meetingRoomsContext}`}
                                        </p>
                                    </div>
                                )}

                                {office.additionalContext && (
                                    <div>
                                        <p className="text-xs font-medium text-gray-700 mb-0">
                                            Additional Context
                                        </p>
                                        <p className="text-sm text-gray-600">
                                            {office.additionalContext}
                                        </p>
                                    </div>
                                )}
                            </div>

                            {/* Right Column - Security Details */}
                            <div className="space-y-4">
                                <div>
                                    <p className="text-xs font-medium text-gray-700 mb-0">
                                        Security Details
                                    </p>
                                    <div className="space-y-2">
                                        {office.checkInRequired && (
                                            <div>
                                                <p className="text-xs text-gray-500 mb-0">
                                                    Check-in Required
                                                </p>
                                                <p className="text-sm text-gray-900 font-medium capitalize">
                                                    {
                                                        YES_NO_OPTIONS.find(
                                                            (opt) =>
                                                                opt.value ===
                                                                office.checkInRequired
                                                        )?.label
                                                    }
                                                </p>
                                            </div>
                                        )}
                                        {office.idRequired && (
                                            <div>
                                                <p className="text-xs text-gray-500 mb-0">
                                                    ID Required
                                                </p>
                                                <p className="text-sm text-gray-900 font-medium capitalize">
                                                    {
                                                        YES_NO_OPTIONS.find(
                                                            (opt) =>
                                                                opt.value ===
                                                                office.idRequired
                                                        )?.label
                                                    }
                                                </p>
                                            </div>
                                        )}
                                        {office.escortRequired && (
                                            <div>
                                                <p className="text-xs text-gray-500 mb-0">
                                                    Escort Required
                                                </p>
                                                <p className="text-sm text-gray-900 font-medium capitalize">
                                                    {
                                                        YES_NO_OPTIONS.find(
                                                            (opt) =>
                                                                opt.value ===
                                                                office.escortRequired
                                                        )?.label
                                                    }
                                                </p>
                                            </div>
                                        )}
                                        {office.securityContext && (
                                            <div>
                                                <p className="text-xs text-gray-500 mb-0">
                                                    Security Context
                                                </p>
                                                <p className="text-sm text-gray-600">
                                                    {office.securityContext}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </>
    );
};

export default OfficeCard;
