import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { endpoints } from "../utils/endpoints";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "../components/ui/dropdown-menu";
import {
    Calendar,
    MapPin,
    Heart,
    Plus,
    Mic,
    ArrowUp,
    Settings,
    Globe,
    User,
    Building,
    Loader2,
    ChevronDown,
    Sparkles,
    Send,
} from "lucide-react";
import { api } from "../utils/api";

const EventDiscovery = () => {
    const [searchQuery, setSearchQuery] = useState("");
    const [locationFilter, setLocationFilter] = useState("Anywhere");
    const [dateFilter, setDateFilter] = useState("Any week");
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showFilters, setShowFilters] = useState(false);
    const [showChatInput, setShowChatInput] = useState(false);
    const [chatPrompt, setChatPrompt] = useState("");
    const [isCreatingProject, setIsCreatingProject] = useState(false);
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        fetchEvents();
    }, []);

    // Show filters when scrolled
    useEffect(() => {
        const handleScroll = () => {
            const scrollPosition = window.scrollY;
            // Show filters when scrolled past the hero section (viewport height minus header)
            const heroHeight = window.innerHeight - 80; // 80px for header
            setShowFilters(scrollPosition > heroHeight * 0.8);
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const fetchEvents = async () => {
        try {
            // Use drew-ai activity endpoint
            const response = await endpoints.activity.list.query();
            // Transform activity data to event format if needed
            setEvents(response.rows || response || []);
        } catch (error) {
            console.error("Failed to fetch events:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleEventClick = (eventId) => {
        navigate(`/event/${eventId}`);
    };

    return (
        <div className="min-h-screen bg-white">
            {/* Top Navigation */}
            <header className="border-b sticky top-0 bg-white z-50">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        {/* Logo */}
                        <img
                            src="/assets/logo-small.png"
                            alt="Drew"
                            className="h-8"
                        />

                        {/* Search Bar - Shows filters when scrolled */}
                        <div className="flex-1 max-w-2xl mx-8">
                            {showFilters ? (
                                <div className="flex items-center gap-2 border rounded-full px-4 py-2 hover:shadow-md transition-shadow">
                                    <button className="text-sm font-medium px-3 py-1 hover:bg-gray-100 rounded-full">
                                        Search
                                    </button>
                                    <div className="h-6 w-px bg-gray-300"></div>
                                    <button className="text-sm font-medium px-3 py-1 hover:bg-gray-100 rounded-full">
                                        {locationFilter}
                                    </button>
                                    <div className="h-6 w-px bg-gray-300"></div>
                                    <button className="text-sm font-medium px-3 py-1 hover:bg-gray-100 rounded-full">
                                        {dateFilter}
                                    </button>
                                </div>
                            ) : (
                                <div className="flex items-center gap-2 border rounded-full px-4 py-2 hover:shadow-md transition-shadow">
                                    <button className="text-sm font-medium px-3 py-1 hover:bg-gray-100 rounded-full">
                                        Search
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Right icons */}
                        <div className="flex items-center gap-4">
                            <Button
                                variant="ghost"
                                size="icon"
                                className="rounded-full"
                            >
                                <Globe className="h-5 w-5" />
                            </Button>
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="rounded-full"
                                    >
                                        <Settings className="h-5 w-5" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                    <DropdownMenuItem
                                        onClick={() => navigate("/profile")}
                                    >
                                        <User className="mr-2 h-4 w-4" />
                                        Profile Settings
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                        onClick={() => {
                                            navigate("/settings/organization");
                                        }}
                                    >
                                        <Building className="mr-2 h-4 w-4" />
                                        Organization Settings
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                        onClick={() => {
                                            // Navigate to model settings
                                            // TODO: Create model settings page
                                            navigate("/profile");
                                        }}
                                    >
                                        <Settings className="mr-2 h-4 w-4" />
                                        Model Settings
                                    </DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="rounded-full bg-gray-100 hover:bg-gray-200"
                                onClick={() => navigate("/profile")}
                                title="Profile"
                            >
                                <User className="h-5 w-5" />
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Hero Section - AI Search */}
            <section className="bg-gradient-to-br from-gray-50 to-white min-h-[calc(100vh-80px)] flex flex-col items-center justify-center border-b relative">
                <div className="max-w-4xl mx-auto px-4 text-center w-full">
                    <div className="inline-flex items-center gap-2 bg-white border border-gray-200 rounded-full px-4 py-2 mb-6">
                        <span className="text-lg">✨</span>
                        <span className="text-sm font-medium">
                            Introducing Drew AI
                        </span>
                    </div>

                    <div className="flex flex-col items-center justify-center mb-4">
                        <h1 className="text-4xl font-bold  text-gray-900">
                            Build your event with{" "}
                            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                                Drew
                            </span>
                        </h1>
                        <p className="text-lg text-gray-600">
                            Find and curate personalized events leveraging AI
                        </p>
                    </div>

                    {/* AI Search Box */}
                    <div className="bg-white rounded-2xl shadow-2xl p-6 w-6xl max-w-full mx-auto border border-gray-100">
                        <div className="mb-4">
                            <Input
                                placeholder="Ask Drew to create an event..."
                                className="h-14 text-base border-0 shadow-none focus-visible:ring-0 px-4"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Button
                                    size="icon"
                                    className="rounded-full h-12 w-12 bg-black hover:bg-gray-800"
                                >
                                    <Plus className="h-5 w-5" />
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="rounded-full gap-2"
                                >
                                    <Calendar className="h-4 w-4" />
                                    Date
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="rounded-full gap-2"
                                >
                                    <MapPin className="h-4 w-4" />
                                    Location
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="rounded-full gap-2"
                                >
                                    <Heart className="h-4 w-4" />
                                    Interests
                                </Button>
                            </div>

                            <div className="flex items-center gap-2">
                                <Button
                                    size="icon"
                                    variant="ghost"
                                    className="rounded-full h-12 w-12"
                                >
                                    <Mic className="h-5 w-5" />
                                </Button>
                                <Button
                                    size="icon"
                                    className="rounded-full h-12 w-12 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                                >
                                    <ArrowUp className="h-5 w-5" />
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Scroll Indicator */}
                <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
                    <div className="flex flex-col items-center gap-2 text-gray-600">
                        <span className="text-sm font-medium">
                            Discover events below
                        </span>
                        <ChevronDown className="h-6 w-6 animate-pulse" />
                    </div>
                </div>
            </section>

            {/* Events Grid */}
            <section className="max-w-7xl mx-auto px-4 py-12 bg-white">
                <div className="mb-8">
                    <h2 className="text-3xl font-bold mb-2 text-gray-900">
                        Discover events near you
                    </h2>
                    <p className="text-gray-600 text-lg">
                        Curated experiences you'll love
                    </p>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center py-20">
                        <Loader2 className="h-12 w-12 animate-spin text-purple-600" />
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {events.map((event) => (
                            <div
                                key={event.id}
                                className="group cursor-pointer"
                                onClick={() => handleEventClick(event.id)}
                            >
                                <div className="relative overflow-hidden rounded-2xl mb-3 aspect-[4/3]">
                                    <img
                                        src={event.images?.[0] || event.thumbnailUrl || 'https://via.placeholder.com/400x300'}
                                        alt={event.title}
                                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                    />
                                    <button className="absolute top-3 right-3 bg-white/90 hover:bg-white rounded-full p-2 backdrop-blur-sm">
                                        <Heart className="h-5 w-5" />
                                    </button>
                                </div>

                                <div className="space-y-1">
                                    <div className="flex items-start justify-between gap-2">
                                        <h3 className="font-semibold text-lg group-hover:underline">
                                            {event.title}
                                        </h3>
                                        <div className="flex items-center gap-1 flex-shrink-0">
                                            <span className="text-sm">★</span>
                                            <span className="text-sm font-medium">
                                                {event.rating}
                                            </span>
                                        </div>
                                    </div>

                                    <p className="text-gray-600 text-sm line-clamp-2">
                                        {event.description}
                                    </p>

                                    <div className="flex items-center gap-2 text-sm text-gray-600">
                                        <MapPin className="h-4 w-4" />
                                        <span>
                                            {event.city}, {event.state}
                                        </span>
                                    </div>

                                    <div className="flex items-baseline gap-1 mt-2">
                                        <span className="font-bold text-lg">
                                            ${event.price}
                                        </span>
                                        <span className="text-gray-600 text-sm">
                                            / guest
                                        </span>
                                    </div>

                                    {event.freeCancellation && (
                                        <Badge
                                            variant="secondary"
                                            className="mt-2"
                                        >
                                            Free cancellation
                                        </Badge>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>
        </div>
    );
};

export default EventDiscovery;
