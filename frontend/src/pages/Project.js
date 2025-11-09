import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { api } from '../utils/api';
import {
    ArrowLeft,
    Send,
    Loader,
    Sparkles,
    Calendar,
    DollarSign,
    Users,
    MapPin,
    CheckCircle
} from 'lucide-react';

const Project = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [recommendations, setRecommendations] = useState([]);
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const messagesEndRef = useRef(null);
    const chatPanelRef = useRef(null);

    useEffect(() => {
        loadProject();
        loadRecommendations();
    }, [projectId]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadProject = async () => {
        try {
            setIsLoading(true);
            const data = await api(`project/${projectId}`, { method: 'GET' });
            setProject(data);
        } catch (error) {
            console.error('Error loading project:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const loadRecommendations = async () => {
        try {
            const data = await api(`recommendation?project_id=${projectId}`, {
                method: 'GET',
            });
            setRecommendations(data.rows || []);
        } catch (error) {
            console.error('Error loading recommendations:', error);
        }
    };

    const sendMessage = async () => {
        if (!inputValue.trim() || isSending) return;

        const userMessage = {
            type: 'user',
            content: inputValue,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputValue('');
        setIsSending(true);

        try {
            // Add loading message
            const loadingMessage = {
                type: 'assistant',
                content: 'Thinking...',
                isLoading: true,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, loadingMessage]);

            const response = await api(`project/${projectId}/chat`, {
                method: 'POST',
                data: { prompt: inputValue },
            });

            // Remove loading message and add actual response
            setMessages((prev) => {
                const filtered = prev.filter((msg) => !msg.isLoading);
                return [
                    ...filtered,
                    {
                        type: 'assistant',
                        content: response.message,
                        recommendations: response.recommendations || [],
                        agentsUsed: response.agentsUsed || [],
                        timestamp: new Date(),
                    },
                ];
            });

            // Reload recommendations if new ones were created
            if (response.recommendations && response.recommendations.length > 0) {
                loadRecommendations();
            }
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages((prev) => {
                const filtered = prev.filter((msg) => !msg.isLoading);
                return [
                    ...filtered,
                    {
                        type: 'assistant',
                        content:
                            'Sorry, I encountered an error. Please try again.',
                        isError: true,
                        timestamp: new Date(),
                    },
                ];
            });
        } finally {
            setIsSending(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Loader className="w-8 h-8 animate-spin text-indigo-600" />
            </div>
        );
    }

    if (!project) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <h2 className="text-2xl font-bold mb-2">Project not found</h2>
                    <button
                        onClick={() => navigate('/projects')}
                        className="text-indigo-600 hover:text-indigo-700"
                    >
                        Back to projects
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-screen bg-gray-50">
            {/* Left Panel - Chat */}
            <div
                ref={chatPanelRef}
                className="w-1/3 bg-white border-r border-gray-200 flex flex-col"
            >
                {/* Header */}
                <div className="p-4 border-b border-gray-200">
                    <button
                        onClick={() => navigate('/discover')}
                        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-3"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        <span>Back to Discovery</span>
                    </button>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">
                            {project.name}
                        </h1>
                        <p className="text-sm text-gray-500 mt-1">
                            {project.description}
                        </p>
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.length === 0 ? (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center text-gray-400">
                                <Sparkles className="w-12 h-12 mx-auto mb-3" />
                                <p className="text-sm">
                                    Ask me to find activities for your project
                                </p>
                            </div>
                        </div>
                    ) : (
                        messages.map((message, idx) => (
                            <div
                                key={idx}
                                className={`flex ${
                                    message.type === 'user'
                                        ? 'justify-end'
                                        : 'justify-start'
                                }`}
                            >
                                <div
                                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                                        message.type === 'user'
                                            ? 'bg-indigo-600 text-white'
                                            : message.isError
                                            ? 'bg-red-50 text-red-900'
                                            : 'bg-gray-100 text-gray-900'
                                    }`}
                                >
                                    {message.isLoading ? (
                                        <div className="flex items-center gap-2">
                                            <Loader className="w-4 h-4 animate-spin" />
                                            <span>Thinking...</span>
                                        </div>
                                    ) : (
                                        <>
                                            <p className="text-sm whitespace-pre-wrap">
                                                {message.content}
                                            </p>
                                            {message.agentsUsed &&
                                                message.agentsUsed.length > 0 && (
                                                    <div className="mt-2 pt-2 border-t border-gray-200">
                                                        <p className="text-xs text-gray-500">
                                                            Agents used:{' '}
                                                            {message.agentsUsed.join(
                                                                ', '
                                                            )}
                                                        </p>
                                                    </div>
                                                )}
                                        </>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-gray-200">
                    <div className="flex gap-2">
                        <textarea
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask me to find activities..."
                            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                            rows="2"
                            disabled={isSending}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={!inputValue.trim() || isSending}
                            className="px-4 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isSending ? (
                                <Loader className="w-5 h-5 animate-spin" />
                            ) : (
                                <Send className="w-5 h-5" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Right Panel - Recommendations */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="max-w-4xl mx-auto">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">
                        Recommendations
                    </h2>

                    {recommendations.length === 0 ? (
                        <div className="text-center py-12">
                            <Sparkles className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                            <p className="text-gray-500">
                                No recommendations yet. Start chatting to get
                                personalized activity recommendations!
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {recommendations.map((rec) => (
                                <div
                                    key={rec.id}
                                    className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
                                >
                                    <div className="flex gap-4 p-4">
                                        {/* Image */}
                                        <div className="flex-shrink-0">
                                            <img
                                                src={
                                                    rec.thumbnailUrl ||
                                                    'https://via.placeholder.com/200x150'
                                                }
                                                alt={rec.title}
                                                className="w-48 h-36 object-cover rounded-xl"
                                            />
                                        </div>

                                        {/* Content */}
                                        <div className="flex-1">
                                            <h3 className="text-xl font-bold text-gray-900 mb-2">
                                                {rec.title}
                                            </h3>
                                            <p className="text-sm text-gray-600 mb-3">
                                                {rec.shortDescription}
                                            </p>

                                            {/* Why recommended */}
                                            {rec.reasonToRecommend && (
                                                <div className="bg-indigo-50 rounded-lg p-3 mb-3">
                                                    <div className="flex items-start gap-2">
                                                        <Sparkles className="w-4 h-4 text-indigo-600 flex-shrink-0 mt-0.5" />
                                                        <p className="text-sm text-indigo-900">
                                                            {rec.reasonToRecommend}
                                                        </p>
                                                    </div>
                                                </div>
                                            )}

                                            {/* Details */}
                                            <div className="flex items-center gap-4 text-sm text-gray-600">
                                                {rec.duration && (
                                                    <div className="flex items-center gap-1">
                                                        <Calendar className="w-4 h-4" />
                                                        <span>
                                                            {Math.round(
                                                                rec.duration / 60
                                                            )}{' '}
                                                            hours
                                                        </span>
                                                    </div>
                                                )}
                                                {rec.score && (
                                                    <div className="flex items-center gap-1">
                                                        <CheckCircle className="w-4 h-4 text-green-600" />
                                                        <span>
                                                            {Math.round(
                                                                rec.score * 100
                                                            )}
                                                            % match
                                                        </span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Project;
