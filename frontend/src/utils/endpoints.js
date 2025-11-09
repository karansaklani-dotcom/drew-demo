/**
 * API Endpoints Configuration
 *
 * This file centralizes all API endpoint definitions for drew-ai backend.
 * Each endpoint includes query functions and cache key generators for React Query.
 */

import { api } from "./api";

export const endpoints = {
    // User Endpoints
    user: {
        register: {
            query: (data) => {
                return api("user/register", {
                    method: "POST",
                    data,
                });
            },
            getKeys: () => ["USER", "REGISTER"],
        },
        verify: {
            query: (data) => {
                return api("user/verify", {
                    method: "POST",
                    data,
                });
            },
            getKeys: () => ["USER", "VERIFY"],
        },
        me: {
            query: () => {
                return api("user/me", {
                    method: "GET",
                });
            },
            getKeys: () => ["USER", "ME"],
        },
        update: {
            query: (id, data) => {
                return api(`user/${id}`, {
                    method: "PUT",
                    data,
                });
            },
            getKeys: (id) => ["USER", "UPDATE", id],
        },
    },

    // Organization Endpoints
    organization: {
        create: {
            query: (data) => {
                return api("organization", {
                    method: "POST",
                    data,
                });
            },
            getKeys: () => ["ORGANIZATION", "CREATE"],
        },
        update: {
            query: (id, data) => {
                return api(`organization/${id}`, {
                    method: "PUT",
                    data,
                });
            },
            getKeys: (id) => ["ORGANIZATION", "UPDATE", id],
        },
        get: {
            query: (id) => {
                return api(`organization/${id}`);
            },
            getKeys: (id) => ["ORGANIZATION", "GET", id],
        },
        list: {
            query: (params) => {
                return api("organization", {
                    method: "GET",
                    params,
                });
            },
            getKeys: (params) => ["ORGANIZATION", "LIST", params],
        },
    },

    // Activity Endpoints (for events)
    activity: {
        list: {
            query: (params) => {
                return api("activity", {
                    method: "GET",
                    params,
                });
            },
            getKeys: (params) => ["ACTIVITY", "LIST", params],
        },
        get: {
            query: (id, expand) => {
                const params = expand ? { expand } : {};
                return api(`activity/${id}`, {
                    method: "GET",
                    params,
                });
            },
            getKeys: (id, expand) => ["ACTIVITY", "GET", id, expand],
        },
        create: {
            query: (data) => {
                return api("activity", {
                    method: "POST",
                    data,
                });
            },
            getKeys: () => ["ACTIVITY", "CREATE"],
        },
        update: {
            query: (id, data) => {
                return api(`activity/${id}`, {
                    method: "PUT",
                    data,
                });
            },
            getKeys: (id) => ["ACTIVITY", "UPDATE", id],
        },
    },

    // Occasion Endpoints
    occasion: {
        list: {
            query: (params) => {
                return api("occasion", {
                    method: "GET",
                    params,
                });
            },
            getKeys: (params) => ["OCCASION", "LIST", params],
        },
        get: {
            query: (id) => {
                return api(`occasion/${id}`);
            },
            getKeys: (id) => ["OCCASION", "GET", id],
        },
    },

    // Offering Endpoints
    offering: {
        list: {
            query: (params) => {
                return api("offering", {
                    method: "GET",
                    params,
                });
            },
            getKeys: (params) => ["OFFERING", "LIST", params],
        },
        get: {
            query: (id) => {
                return api(`offering/${id}`);
            },
            getKeys: (id) => ["OFFERING", "GET", id],
        },
    },

    // Onboarding Endpoints
    onboarding: {
        complete: {
            query: (data) => {
                return api("onboarding", {
                    method: "POST",
                    data,
                });
            },
            getKeys: () => ["ONBOARDING", "COMPLETE"],
        },
    },
};
