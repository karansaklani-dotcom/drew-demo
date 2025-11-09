import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
import { Button } from '../components/ui/button';
import {
    ArrowLeft,
    Calendar,
    Clock,
    Users,
    DollarSign,
    MapPin,
    Heart,
    Share2,
    Star,
    Sparkles,
    CheckCircle,
    X
} from 'lucide-react';

const RecommendationDetail = () => {
    const { projectId, recommendationId } = useParams();
    const navigate = useNavigate();
    const [recommendation, setRecommendation] = useState(null);
    const [activity, setActivity] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeImage, setActiveImage] = useState(0);

    useEffect(() => {
        loadRecommendation();
    }, [recommendationId]);

    const loadRecommendation = async () => {
        try {
            setLoading(true);
            // Fetch recommendation with expanded activity details
            const response = await api.get(`/api/recommendation/${recommendationId}?expand=activity`);
            setRecommendation(response.data);
            
            // Activity details should be in activityDetails from backend
            if (response.data.activityDetails) {
                setActivity(response.data.activityDetails);
            }
        } catch (error) {
            console.error('Error loading recommendation:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-white flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (!recommendation) {
        return (
            <div className="min-h-screen bg-white flex items-center justify-center">
                <div className="text-center">
                    <p className="text-gray-600 mb-4">Recommendation not found</p>
                    <Button onClick={() => navigate(`/project/${projectId}`)}>
                        Back to Project
                    </Button>
                </div>
            </div>
        );
    }

    const images = activity?.images || [recommendation.thumbnailUrl] || [];
    const currentImage = images[activeImage] || 'https://via.placeholder.com/800x600';

    return (
        <div className="min-h-screen bg-white">
            {/* Header */}
            <header className="border-b sticky top-0 bg-white z-50">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => navigate(`/project/${projectId}`)}
                            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
                        >
                            <ArrowLeft className="w-5 h-5" />
                            <span className="font-medium">Back to Project</span>
                        </button>
                        <div className="flex items-center gap-2">
                            <Button variant="ghost" size="icon">
                                <Share2 className="w-5 h-5" />
                            </Button>
                            <Button variant="ghost" size="icon">
                                <Heart className="w-5 h-5" />
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left Panel - Images & Title */}
                    <div className="space-y-6">
                        {/* Main Image */}
                        <div className="relative aspect-[4/3] rounded-2xl overflow-hidden">
                            <img
                                src={currentImage}
                                alt={recommendation.title}
                                className="w-full h-full object-cover"
                            />
                            {images.length > 1 && (
                                <>
                                    <button
                                        onClick={() => setActiveImage((prev) => (prev > 0 ? prev - 1 : images.length - 1))}
                                        className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white rounded-full p-2 backdrop-blur-sm"
                                    >
                                        <ArrowLeft className="w-5 h-5" />
                                    </button>
                                    <button
                                        onClick={() => setActiveImage((prev) => (prev < images.length - 1 ? prev + 1 : 0))}
                                        className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white rounded-full p-2 backdrop-blur-sm rotate-180"
                                    >
                                        <ArrowLeft className="w-5 h-5" />
                                    </button>
                                </>
                            )}
                        </div>

                        {/* Thumbnail Gallery */}
                        {images.length > 1 && (
                            <div className="grid grid-cols-4 gap-3">
                                {images.slice(0, 4).map((image, index) => (
                                    <button
                                        key={index}
                                        onClick={() => setActiveImage(index)}
                                        className={`aspect-[4/3] rounded-lg overflow-hidden border-2 transition-all ${
                                            activeImage === index
                                                ? 'border-indigo-600'
                                                : 'border-transparent hover:border-gray-300'
                                        }`}
                                    >
                                        <img
                                            src={image}
                                            alt={`View ${index + 1}`}
                                            className="w-full h-full object-cover"
                                        />
                                    </button>
                                ))}
                            </div>
                        )}

                        {/* Title & Host */}
                        <div className="space-y-4">
                            <div>
                                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                                    {recommendation.customizedTitle || recommendation.title}
                                </h1>
                                {recommendation.customizedTitle && (
                                    <p className="text-sm text-gray-500 mb-2">
                                        Original: {recommendation.title}
                                    </p>
                                )}
                                {activity?.host && (
                                    <p className="text-gray-600">
                                        Hosted by <span className="font-semibold">{activity.host.name}</span>
                                        {activity.host.title && ` • ${activity.host.title}`}
                                    </p>
                                )}
                            </div>

                            {/* Why Recommended - Prominent */}
                            {recommendation.reasonToRecommend && (
                                <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4">
                                    <div className="flex items-start gap-3">
                                        <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                                            <Sparkles className="w-4 h-4 text-indigo-600" />
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="font-semibold text-indigo-900 mb-1">
                                                Why Drew recommends this
                                            </h3>
                                            <p className="text-indigo-800 text-sm">
                                                {recommendation.reasonToRecommend}
                                            </p>
                                            {recommendation.score && (
                                                <div className="flex items-center gap-2 mt-2">
                                                    <CheckCircle className="w-4 h-4 text-green-600" />
                                                    <span className="text-sm font-medium text-gray-700">
                                                        {Math.round(recommendation.score * 100)}% match for your needs
                                                    </span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Description */}
                            <div className="space-y-3">
                                <h2 className="text-xl font-bold text-gray-900">About this activity</h2>
                                <p className="text-gray-700 leading-relaxed">
                                    {recommendation.longDescription || recommendation.shortDescription}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Right Panel - Details & Booking */}
                    <div className="space-y-6">
                        {/* Stats Grid */}
                        <div className="grid grid-cols-2 gap-4">
                            {recommendation.duration && (
                                <div className="bg-gray-50 rounded-xl p-4">
                                    <div className="flex items-center gap-2 text-gray-600 mb-1">
                                        <Clock className="w-4 h-4" />
                                        <span className="text-sm font-medium">Duration</span>
                                    </div>
                                    <p className="text-lg font-bold text-gray-900">
                                        {Math.round(recommendation.duration / 60)} hours
                                    </p>
                                </div>
                            )}
                            {activity?.minParticipants && (
                                <div className="bg-gray-50 rounded-xl p-4">
                                    <div className="flex items-center gap-2 text-gray-600 mb-1">
                                        <Users className="w-4 h-4" />
                                        <span className="text-sm font-medium">Group Size</span>
                                    </div>
                                    <p className="text-lg font-bold text-gray-900">
                                        {activity.minParticipants}-{activity.maxParticipants} people
                                    </p>
                                </div>
                            )}
                            {activity?.city && (
                                <div className="bg-gray-50 rounded-xl p-4 col-span-2">
                                    <div className="flex items-center gap-2 text-gray-600 mb-1">
                                        <MapPin className="w-4 h-4" />
                                        <span className="text-sm font-medium">Location</span>
                                    </div>
                                    <p className="text-lg font-bold text-gray-900">
                                        {activity.city}, {activity.state}
                                    </p>
                                    {activity.location && (
                                        <p className="text-sm text-gray-600 mt-1">{activity.location}</p>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Customized Itinerary */}
                        {recommendation.itinerary && recommendation.itinerary.length > 0 && (
                            <div className="bg-white border border-gray-200 rounded-xl p-6">
                                <h2 className="text-xl font-bold text-gray-900 mb-4">Customized Itinerary</h2>
                                <div className="space-y-4">
                                    {recommendation.itinerary.map((item, index) => (
                                        <div key={index} className="flex gap-4">
                                            <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                                                <span className="text-sm font-bold text-indigo-600">
                                                    {index + 1}
                                                </span>
                                            </div>
                                            <div className="flex-1">
                                                <h3 className="font-semibold text-gray-900">
                                                    {item.title}
                                                </h3>
                                                <p className="text-sm text-gray-600 mt-1">
                                                    {item.description}
                                                </p>
                                                {item.duration && (
                                                    <p className="text-xs text-gray-500 mt-1">
                                                        {item.duration} minutes
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* What's Included */}
                        {activity?.included && activity.included.length > 0 && (
                            <div className="bg-white border border-gray-200 rounded-xl p-6">
                                <h2 className="text-xl font-bold text-gray-900 mb-4">What's Included</h2>
                                <div className="space-y-2">
                                    {activity.included.map((item, index) => (
                                        <div key={index} className="flex items-center gap-2">
                                            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                                            <span className="text-gray-700">{item.title}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Prerequisites */}
                        {activity?.preRequisites && activity.preRequisites.length > 0 && (
                            <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
                                <h2 className="text-xl font-bold text-gray-900 mb-4">What to Bring</h2>
                                <div className="space-y-2">
                                    {activity.preRequisites.map((item, index) => (
                                        <div key={index} className="flex items-start gap-2">
                                            <div className="w-5 h-5 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                                <span className="text-xs text-amber-700">!</span>
                                            </div>
                                            <span className="text-gray-700">{item.title || item.name}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Action Button */}
                        <Button 
                            className="w-full h-12 text-base"
                            onClick={() => {
                                // Future: Add to cart or booking flow
                                alert('Booking functionality coming soon!');
                            }}
                        >
                            Add to Itinerary
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RecommendationDetail;
