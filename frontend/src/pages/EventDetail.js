import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { endpoints } from "../utils/endpoints";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Separator } from "../components/ui/separator";
import {
    ArrowLeft,
    Share2,
    Heart,
    MapPin,
    Star,
    User,
    Calendar,
    ShieldCheck,
    CreditCard,
    Footprints,
    Cloud,
    Music,
    Wine,
    BookOpen,
    UtensilsCrossed,
    Palette,
    Volume2,
    Smile,
    Shirt,
    Loader2,
} from "lucide-react";

const iconMap = {
    MapPin,
    Music,
    Wine,
    BookOpen,
    ShieldCheck,
    CreditCard,
    Footprints,
    Cloud,
    UtensilsCrossed,
    Palette,
    Volume2,
    Smile,
    Shirt,
    Heart,
};

const EventDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [event, setEvent] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchEvent();
    }, [id]);

    const fetchEvent = async () => {
        try {
            // Use drew-ai activity endpoint
            const eventData = await endpoints.activity.get.query(id);
            setEvent(eventData);
        } catch (error) {
            console.error("Failed to fetch event:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="h-12 w-12 animate-spin text-purple-600" />
            </div>
        );
    }

    if (!event) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold mb-4">Event not found</h2>
                    <Button onClick={() => navigate("/")}>
                        Back to events
                    </Button>
                </div>
            </div>
        );
    }

    const getIcon = (iconName) => {
        const Icon = iconMap[iconName] || MapPin;
        return <Icon className="h-5 w-5 text-gray-600" />;
    };

    return (
        <div className="min-h-screen bg-white">
            {/* Header */}
            <header className="border-b sticky top-0 bg-white z-50">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <Button
                            variant="ghost"
                            onClick={() => navigate("/")}
                            className="gap-2"
                        >
                            <ArrowLeft className="h-4 w-4" />
                            Back
                        </Button>

                        <div className="flex items-center gap-2">
                            <Button variant="ghost" className="gap-2">
                                <Share2 className="h-4 w-4" />
                                Share
                            </Button>
                            <Button variant="ghost" className="gap-2">
                                <Heart className="h-4 w-4" />
                                Save
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Image Gallery */}
            <div className="max-w-7xl mx-auto px-4 py-6">
                {event.images.length === 1 ? (
                    <div className="rounded-2xl overflow-hidden max-h-[500px]">
                        <img
                            src={event.images[0]}
                            alt={event.title}
                            className="w-full max-w-full h-auto max-h-[500px] object-contain"
                        />
                    </div>
                ) : event.images.length === 2 ? (
                    <div className="grid grid-cols-2 gap-4 max-h-[500px]">
                        {event.images.map((img, idx) => (
                            <div
                                key={idx}
                                className="rounded-2xl overflow-hidden"
                            >
                                <img
                                    src={img}
                                    alt={`${event.title} ${idx + 1}`}
                                    className="w-full max-w-full h-auto max-h-[500px] object-cover"
                                />
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="grid grid-cols-2 gap-4 max-h-[500px]">
                        <div className="rounded-2xl overflow-hidden col-span-1 row-span-2">
                            <img
                                src={event.images[0]}
                                alt={event.title}
                                className="w-full max-w-full h-full max-h-[500px] object-cover"
                            />
                        </div>
                        <div className="grid grid-rows-2 gap-4">
                            {event.images.slice(1, 3).map((img, idx) => (
                                <div
                                    key={idx}
                                    className="rounded-2xl overflow-hidden"
                                >
                                    <img
                                        src={img}
                                        alt={`${event.title} ${idx + 2}`}
                                        className="w-full max-w-full h-auto max-h-[240px] object-cover"
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Content */}
            <div className="max-w-7xl mx-auto px-4 pb-12">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-8">
                        {/* Title Section */}
                        <div>
                            <h1 className="text-4xl font-bold mb-4">
                                {event.title}
                            </h1>
                            <p className="text-gray-600 text-lg mb-4">
                                {event.description}
                            </p>

                            <div className="flex items-center gap-4 text-sm">
                                <div className="flex items-center gap-1">
                                    <Star className="h-4 w-4 fill-black" />
                                    <span className="font-semibold">
                                        {event.rating}
                                    </span>
                                    <span className="text-gray-600">
                                        · {event.reviewCount.toLocaleString()}{" "}
                                        reviews
                                    </span>
                                </div>
                                <span className="text-gray-600">·</span>
                                <span className="text-gray-600">
                                    {event.city}
                                </span>
                                <span className="text-gray-600">·</span>
                                <span className="text-gray-600">
                                    {event.category}
                                </span>
                            </div>
                        </div>

                        <Separator />

                        {/* About Section */}
                        <div>
                            <h2 className="text-2xl font-bold mb-4">About</h2>
                            <p className="text-gray-700 leading-relaxed">
                                {event.longDescription}
                            </p>
                        </div>

                        {/* What's included */}
                        {event.included && event.included.length > 0 && (
                            <>
                                <Separator />
                                <div>
                                    <h2 className="text-2xl font-bold mb-6">
                                        What's included
                                    </h2>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {event.included.map((item, idx) => (
                                            <div
                                                key={idx}
                                                className="flex gap-4"
                                            >
                                                <div className="flex-shrink-0">
                                                    {getIcon(item.icon)}
                                                </div>
                                                <div>
                                                    <p className="text-gray-900">
                                                        {item.title}
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </>
                        )}

                        {/* What's required */}
                        {event.required && event.required.length > 0 && (
                            <>
                                <Separator />
                                <div>
                                    <h2 className="text-2xl font-bold mb-6">
                                        What's required
                                    </h2>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {event.required.map((item, idx) => (
                                            <div
                                                key={idx}
                                                className="flex gap-4"
                                            >
                                                <div className="flex-shrink-0">
                                                    {getIcon(item.icon)}
                                                </div>
                                                <div>
                                                    <p className="text-gray-900">
                                                        {item.title}
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </>
                        )}

                        {/* What you'll do */}
                        {event.itinerary && event.itinerary.length > 0 && (
                            <>
                                <Separator />
                                <div>
                                    <h2 className="text-2xl font-bold mb-6">
                                        What you'll do
                                    </h2>
                                    <div className="space-y-6">
                                        {event.itinerary.map((item, idx) => (
                                            <div
                                                key={idx}
                                                className="flex gap-4"
                                            >
                                                <div className="flex-shrink-0">
                                                    <img
                                                        src={item.image}
                                                        alt={item.title}
                                                        className="w-20 h-20 rounded-xl object-cover"
                                                    />
                                                </div>
                                                <div className="flex-1">
                                                    <h3 className="font-semibold text-lg mb-1">
                                                        {item.title}
                                                    </h3>
                                                    <p className="text-gray-600">
                                                        {item.description}
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </>
                        )}
                    </div>

                    {/* Sidebar - Booking Card */}
                    <div className="lg:col-span-1">
                        <div className="sticky top-24">
                            <div className="border rounded-2xl p-6 shadow-xl">
                                <div className="flex items-baseline justify-between mb-4">
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-3xl font-bold">
                                            ${event.price}
                                        </span>
                                        <span className="text-gray-600">
                                            / guest
                                        </span>
                                    </div>
                                </div>

                                {event.freeCancellation && (
                                    <p className="text-sm text-gray-600 mb-4 underline">
                                        Free cancellation
                                    </p>
                                )}

                                <Button className="w-full h-12 bg-black hover:bg-gray-800 text-white font-semibold mb-4">
                                    Show dates
                                </Button>

                                <Separator className="my-6" />

                                {/* Host Info */}
                                <div>
                                    <h3 className="font-semibold text-lg mb-4">
                                        Hosted by {event.host.name}
                                    </h3>
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="w-12 h-12 rounded-full overflow-hidden bg-gray-200">
                                            <img
                                                src={event.host.avatar}
                                                alt={event.host.name}
                                                className="w-full h-full object-cover"
                                            />
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-sm text-gray-600">
                                                {event.host.title}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <Separator className="my-6" />

                                {/* Location Info */}
                                <div>
                                    <h3 className="font-semibold text-lg mb-2">
                                        {event.location}
                                    </h3>
                                    <div className="flex items-center gap-2 text-gray-600">
                                        <MapPin className="h-4 w-4" />
                                        <span className="text-sm">
                                            {event.city}, {event.state}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EventDetail;
