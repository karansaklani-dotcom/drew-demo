// Suppress ResizeObserver errors - these are harmless and occur with Radix UI components
// This error occurs when ResizeObserver detects size changes faster than it can process them
// MUST be defined before React imports to catch errors early
const isResizeObserverError = (error) => {
    if (!error) return false;

    // Check multiple formats
    const errorString =
        typeof error === "string"
            ? error
            : error?.message || error?.toString() || "";

    // Also check stack trace if available
    const stackTrace = error?.stack || "";

    const checkString = (errorString + " " + stackTrace).toLowerCase();

    return (
        checkString.includes(
            "resizeobserver loop completed with undelivered notifications"
        ) ||
        checkString.includes("resizeobserver loop limit exceeded") ||
        checkString.includes("resizeobserver")
    );
};

// Set up error suppression BEFORE React imports
if (typeof window !== "undefined") {
    // Suppress in console.error and console.warn
    const originalError = console.error;
    const originalWarn = console.warn;

    console.error = (...args) => {
        // Check all arguments including Error objects
        const hasResizeObserverError = args.some((arg) => {
            if (isResizeObserverError(arg)) return true;
            // Also check if it's an Error object with ResizeObserver in stack
            if (arg instanceof Error && arg.stack) {
                return isResizeObserverError(arg);
            }
            return false;
        });

        if (hasResizeObserverError) {
            return;
        }
        originalError.apply(console, args);
    };

    console.warn = (...args) => {
        if (args.some((arg) => isResizeObserverError(arg))) {
            return;
        }
        originalWarn.apply(console, args);
    };

    // Suppress in window error handler
    const originalErrorHandler = window.onerror;
    window.onerror = (message, source, lineno, colno, error) => {
        if (isResizeObserverError(message) || isResizeObserverError(error)) {
            return true; // Prevent default error handling
        }
        if (originalErrorHandler) {
            return originalErrorHandler(message, source, lineno, colno, error);
        }
        return false;
    };

    // Handle error events with capture phase
    window.addEventListener(
        "error",
        (event) => {
            if (
                isResizeObserverError(event.message) ||
                isResizeObserverError(event.error)
            ) {
                event.preventDefault();
                event.stopImmediatePropagation();
                event.stopPropagation();
                return false;
            }
        },
        true // Use capture phase to catch early
    );

    // Handle unhandled promise rejections
    window.addEventListener("unhandledrejection", (event) => {
        if (isResizeObserverError(event.reason)) {
            event.preventDefault();
            return false;
        }
    });

    // Override React's error handler if it exists (for development mode)
    if (window.__REACT_ERROR_OVERLAY_GLOBAL_HOOK__) {
        const originalError =
            window.__REACT_ERROR_OVERLAY_GLOBAL_HOOK__.onError;
        if (originalError) {
            window.__REACT_ERROR_OVERLAY_GLOBAL_HOOK__.onError = (error) => {
                if (isResizeObserverError(error)) {
                    return;
                }
                originalError(error);
            };
        }
    }
}

import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
