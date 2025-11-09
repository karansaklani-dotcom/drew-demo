/**
 * API Utility Module
 *
 * This module provides a centralized API client for making HTTP requests to drew-ai backend.
 * All API calls should go through this utility to ensure consistency.
 */

import axios from "axios";

const BACKEND_URL =
    process.env.REACT_APP_DREW_AI_BACKEND_URL || "http://localhost:3000";
const REDIRECT_PATH_KEY = "redirect_path";
const TOKEN_KEY = "auth_token";

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: BACKEND_URL,
    withCredentials: false, // Changed to false for JWT-based auth
    headers: {
        "Content-Type": "application/json",
    },
});

// Request interceptor to add JWT token
apiClient.interceptors.request.use(
    (config) => {
        // Get token from localStorage
        const token = localStorage.getItem(TOKEN_KEY);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => {
        // Check if response contains a token and store it
        if (response.data?.token) {
            localStorage.setItem(TOKEN_KEY, response.data.token);
        }
        return response;
    },
    (error) => {
        if (error.response?.status === 401) {
            // Unauthorized - clear token and redirect to login
            localStorage.removeItem(TOKEN_KEY);
            if (window.location.pathname !== "/login") {
                localStorage.setItem(
                    REDIRECT_PATH_KEY,
                    window.location.pathname
                );
                window.location.replace("/login");
            }
        }
        return Promise.reject(error);
    }
);

/**
 * API function for making requests
 * @param {string} endpoint - API endpoint (e.g., "user/register")
 * @param {object} options - Request options
 * @param {object} options.data - Request body data
 * @param {string} options.method - HTTP method (GET, POST, PUT, DELETE, etc.)
 * @param {object} options.headers - Additional headers
 * @param {object} options.params - Query parameters
 * @returns {Promise} API response
 */
function api(endpoint, options = {}) {
    const { data, method = "GET", headers = {}, params, ...rest } = options;

    const config = {
        method,
        url: endpoint,
        headers,
        ...rest,
    };

    if (data) {
        config.data = data;
    }

    if (params) {
        config.params = params;
    }

    return apiClient(config).then((response) => response.data);
}

export { api, apiClient };
