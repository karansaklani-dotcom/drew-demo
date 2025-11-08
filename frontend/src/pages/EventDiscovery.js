import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Calendar, MapPin, Heart, Plus, Mic, ArrowUp, Menu, Globe, User, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EventDiscovery = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [locationFilter, setLocationFilter] = useState('Anywhere');
  const [dateFilter, setDateFilter] = useState('Any week');
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await axios.get(`${API}/events`);
      setEvents(response.data.events);
    } catch (error) {
      console.error('Failed to fetch events:', error);
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
            <div className="bg-black text-white px-4 py-2 rounded-lg text-xl font-bold">
              Drew
            </div>

            {/* Search Bar */}
            <div className="flex-1 max-w-2xl mx-8">
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
            </div>

            {/* Right icons */}
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" className="rounded-full">
                <Globe className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon" className="rounded-full">
                <Menu className="h-5 w-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full bg-gray-100 hover:bg-gray-200"
                onClick={logout}
              >
                <User className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section - AI Search */}
      <section className="bg-gradient-to-br from-gray-50 to-white py-20 border-b">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="inline-flex items-center gap-2 bg-white border border-gray-200 rounded-full px-4 py-2 mb-6">
            <span className="text-lg">✨</span>
            <span className="text-sm font-medium">Introducing Drew AI</span>
          </div>

          <h1 className="text-5xl font-bold mb-4">
            Build your event with{' '}
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Drew
            </span>
          </h1>

          <p className="text-gray-600 text-lg mb-12">
            Find and curate personalised events with AI
          </p>

          {/* AI Search Box */}
          <div className="bg-white rounded-2xl shadow-2xl p-6 max-w-2xl mx-auto border border-gray-100">
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
                <Button variant="outline" size="sm" className="rounded-full gap-2">
                  <Calendar className="h-4 w-4" />
                  Date
                </Button>
                <Button variant="outline" size="sm" className="rounded-full gap-2">
                  <MapPin className="h-4 w-4" />
                  Location
                </Button>
                <Button variant="outline" size="sm" className="rounded-full gap-2">
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
      </section>

      {/* Events Grid */}
      <section className="max-w-7xl mx-auto px-4 py-12">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-2">Discover events near you</h2>
          <p className="text-gray-600">Curated experiences you'll love</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockEvents.map((event) => (
            <div
              key={event.id}
              className="group cursor-pointer"
              onClick={() => handleEventClick(event.id)}
            >
              <div className="relative overflow-hidden rounded-2xl mb-3 aspect-square">
                <img
                  src={event.images[0]}
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
                    <span className="text-sm font-medium">{event.rating}</span>
                  </div>
                </div>

                <p className="text-gray-600 text-sm line-clamp-2">
                  {event.description}
                </p>

                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <MapPin className="h-4 w-4" />
                  <span>{event.city}, {event.state}</span>
                </div>

                <div className="flex items-baseline gap-1 mt-2">
                  <span className="font-bold text-lg">${event.price}</span>
                  <span className="text-gray-600 text-sm">/ guest</span>
                </div>

                {event.freeCancellation && (
                  <Badge variant="secondary" className="mt-2">
                    Free cancellation
                  </Badge>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default EventDiscovery;
