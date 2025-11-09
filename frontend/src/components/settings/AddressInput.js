import React, { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Button } from "../ui/button";
import { useToast } from "../../hooks/use-toast";
import usePlacesAutocomplete, {
    getGeocode,
    getLatLng,
} from "use-places-autocomplete";
import useGoogleMaps from "../../hooks/use-google-maps";

const AddressInput = ({ value, onChange }) => {
    const { toast } = useToast();
    const { isLoaded, error } = useGoogleMaps();
    const [address, setAddress] = useState(
        value || {
            line1: "",
            line2: "",
            city: "",
            country: "",
            pincode: "",
        }
    );

    const {
        ready,
        value: autocompleteValue,
        suggestions: { status, data },
        setValue: setAutocompleteValue,
        clearSuggestions,
    } = usePlacesAutocomplete({
        requestOptions: {
            types: ["address"],
        },
        debounce: 300,
    });

    useEffect(() => {
        if (value) {
            setAddress(value);
        }
    }, [value]);

    const handleSelect = async (suggestion) => {
        const {
            place_id,
            structured_formatting: { main_text, secondary_text },
        } = suggestion;

        setAutocompleteValue(suggestion.description, false);
        clearSuggestions();

        try {
            const results = await getGeocode({ placeId: place_id });
            const { lat, lng } = await getLatLng(results[0]);
            const addressComponents = results[0].address_components;

            const newAddress = parseAddressComponents(addressComponents);

            // Use main_text as line1 if parsing didn't produce a good result
            if (!newAddress.line1 || newAddress.line1.trim() === "") {
                newAddress.line1 = main_text || results[0].formatted_address;
            }

            // Use secondary_text for line2 if available and line2 is empty
            if (!newAddress.line2 && secondary_text) {
                newAddress.line2 = secondary_text;
            }

            setAddress(newAddress);
            onChange(newAddress);

            toast({
                title: "Address filled",
                description:
                    "Address details have been prefilled from Google Maps",
            });
        } catch (error) {
            console.error("Error getting place details:", error);
            toast({
                variant: "destructive",
                title: "Error",
                description: "Failed to get address details. Please try again.",
            });
        }
    };

    const parseAddressComponents = (components) => {
        const address = {
            line1: "",
            line2: "",
            city: "",
            country: "",
            pincode: "",
        };

        let streetNumber = "";
        let route = "";

        components.forEach((component) => {
            const types = component.types;
            const longName = component.long_name;

            if (types.includes("street_number")) {
                streetNumber = longName;
            } else if (types.includes("route")) {
                route = longName;
            } else if (
                types.includes("subpremise") ||
                types.includes("premise")
            ) {
                if (!address.line2) {
                    address.line2 = longName;
                }
            } else if (types.includes("locality")) {
                address.city = longName;
            } else if (types.includes("postal_town") && !address.city) {
                address.city = longName;
            } else if (types.includes("postal_code")) {
                address.pincode = longName;
            } else if (types.includes("country")) {
                address.country = longName;
            }
        });

        // Combine street number and route for line1
        if (streetNumber && route) {
            address.line1 = `${streetNumber} ${route}`;
        } else if (route) {
            address.line1 = route;
        } else if (streetNumber) {
            address.line1 = streetNumber;
        }

        return address;
    };

    const handleChange = (field, fieldValue) => {
        const newAddress = { ...address, [field]: fieldValue };
        setAddress(newAddress);
        onChange(newAddress);
    };

    const handleLine1Change = (e) => {
        const value = e.target.value;
        setAutocompleteValue(value);
        handleChange("line1", value);
    };

    const handleGoogleMapsSearch = () => {
        if (error) {
            toast({
                variant: "destructive",
                title: "Google Maps Error",
                description: error,
            });
            return;
        }

        if (!isLoaded || !ready) {
            toast({
                variant: "destructive",
                title: "Loading...",
                description:
                    "Google Maps is still loading. Please wait a moment.",
            });
            return;
        }

        // Focus the Address Line 1 input
        const line1Input = document.getElementById("line1");
        if (line1Input) {
            line1Input.focus();
            toast({
                title: "Start typing",
                description:
                    "Begin typing an address in the Address Line 1 field to see suggestions",
            });
        }
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
                <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleGoogleMapsSearch}
                    className="border-gray-300"
                    disabled={!isLoaded || !!error || !ready}
                >
                    <Search className="mr-2 h-4 w-4" />
                    {isLoaded && ready
                        ? "Search with Google Maps"
                        : "Loading Maps..."}
                </Button>
                {error && <p className="text-xs text-red-500">{error}</p>}
                {isLoaded && !error && ready && (
                    <p className="text-xs text-gray-500">
                        Start typing in Address Line 1 to see suggestions
                    </p>
                )}
            </div>

            <div className="space-y-4">
                <div className="space-y-2">
                    <div className="flex flex-col items-start gap-1">
                        <Label htmlFor="line1">
                            Address Line 1{" "}
                            <span className="text-red-500">*</span>
                        </Label>
                        <p className="text-xs text-gray-500 mb-1">
                            {isLoaded && ready
                                ? "Start typing an address to see Google Maps suggestions"
                                : "Street address, P.O. box, or company name"}
                        </p>
                    </div>
                    <div className="relative">
                        <Input
                            id="line1"
                            value={autocompleteValue || address.line1}
                            onChange={handleLine1Change}
                            placeholder="Start typing an address..."
                            disabled={!ready}
                            autoComplete="off"
                        />
                        {status === "OK" && data.length > 0 && (
                            <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
                                {data.map((suggestion) => {
                                    const {
                                        place_id,
                                        structured_formatting: {
                                            main_text,
                                            secondary_text,
                                        },
                                    } = suggestion;
                                    return (
                                        <button
                                            key={place_id}
                                            type="button"
                                            onClick={() =>
                                                handleSelect(suggestion)
                                            }
                                            className="w-full text-left px-4 py-2 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
                                        >
                                            <div className="font-medium text-sm text-gray-900">
                                                {main_text}
                                            </div>
                                            {secondary_text && (
                                                <div className="text-xs text-gray-500">
                                                    {secondary_text}
                                                </div>
                                            )}
                                        </button>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>

                <div className="space-y-2">
                    <div className="flex flex-col items-start gap-1">
                        <Label htmlFor="line2">Address Line 2</Label>
                        <p className="text-xs text-gray-500 mb-1">
                            Apartment, suite, unit, building, floor, etc.
                            (optional)
                        </p>
                    </div>
                    <Input
                        id="line2"
                        value={address.line2}
                        onChange={(e) => handleChange("line2", e.target.value)}
                        placeholder="Apartment, suite, unit, building, floor, etc."
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <div className="flex flex-col items-start gap-1">
                            <Label htmlFor="city">
                                City <span className="text-red-500">*</span>
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                City or town name
                            </p>
                        </div>
                        <Input
                            id="city"
                            value={address.city}
                            onChange={(e) =>
                                handleChange("city", e.target.value)
                            }
                            placeholder="City"
                        />
                    </div>

                    <div className="space-y-2">
                        <div className="flex flex-col items-start gap-1">
                            <Label htmlFor="pincode">
                                Pincode <span className="text-red-500">*</span>
                            </Label>
                            <p className="text-xs text-gray-500 mb-1">
                                ZIP or postal code
                            </p>
                        </div>
                        <Input
                            id="pincode"
                            value={address.pincode}
                            onChange={(e) =>
                                handleChange("pincode", e.target.value)
                            }
                            placeholder="ZIP/Postal code"
                        />
                    </div>
                </div>

                <div className="space-y-2">
                    <div className="flex flex-col items-start gap-1">
                        <Label htmlFor="country">
                            Country <span className="text-red-500">*</span>
                        </Label>
                        <p className="text-xs text-gray-500 mb-1">
                            Country name
                        </p>
                    </div>
                    <Input
                        id="country"
                        value={address.country}
                        onChange={(e) =>
                            handleChange("country", e.target.value)
                        }
                        placeholder="Country"
                    />
                </div>
            </div>
        </div>
    );
};

export default AddressInput;
