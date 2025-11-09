import { useEffect, useState } from "react";

const useGoogleMaps = () => {
    const [isLoaded, setIsLoaded] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const apiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

        if (!apiKey) {
            setError("Google Maps API key is not configured");
            return;
        }

        // Check if Google Maps is already loaded
        if (window.google && window.google.maps && window.google.maps.places) {
            setIsLoaded(true);
            return;
        }

        // Check if script is already being loaded
        const existingScript = document.querySelector(
            'script[src*="maps.googleapis.com"]'
        );
        if (existingScript) {
            existingScript.addEventListener("load", () => {
                setIsLoaded(true);
            });
            return;
        }

        // Load Google Maps JavaScript API with Places library
        const script = document.createElement("script");
        script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
        script.async = true;
        script.defer = true;

        script.addEventListener("load", () => {
            setIsLoaded(true);
        });

        script.addEventListener("error", () => {
            setError("Failed to load Google Maps API");
        });

        document.head.appendChild(script);

        return () => {
            // Cleanup: remove script if component unmounts
            const scriptToRemove = document.querySelector(
                'script[src*="maps.googleapis.com"]'
            );
            if (scriptToRemove) {
                scriptToRemove.remove();
            }
        };
    }, []);

    return { isLoaded, error };
};

export default useGoogleMaps;
